# Run with "python server.py"
"""
Starts and keeps the server running. Handles requests.
"""
import datetime
import json
from hashlib import md5

import jwt

from bottle import run, route, request, hook, HTTPResponse
from peewee import *
from playhouse.shortcuts import model_to_dict


# Start your code here, good luck (: ...
db = SqliteDatabase('content.db')
KEY = 'MIIBVAIBADANBgkqhkiG9w0BAQEFAASCAT4wggE6AgEAAkEAkgDUAAjZUpWw9z'


class BaseModel(Model):
    """Base Model to specifiy in only one place which database to use.
    """
    class Meta:
        """Defining which database to use. Is extended by other models.
        """
        database = db


class User(BaseModel):
    """User model
    username is unique.  Id is also added by default for indexing.

    """
    username = CharField(unique=True)
    password = CharField()
    email = CharField()


class Notes(BaseModel):
    """Notes Model
    user is foreign key to User model, Id added by default
    """
    user = ForeignKeyField(User, backref='notes')
    title = CharField()
    content = TextField()


@hook('before_request')
def before_request():
    """Open connection before each request
    """
    db.connect()


@hook('after_request')
def after_request():
    """Close connection after each request
    """
    db.close()


def create_tables():
    """creates tables if not created
    """
    with db:
        db.create_tables([User, Notes])


@route('/create-user', method='POST')
def create_user():
    """POST to create user
    Takes in JSON with username, password, and email
    returns error if user already exists
    """
    try:
        body = request.json
        with db.atomic():
            user = User.create(
                username=body.get('username'),
                password=md5(body.get('password').encode('utf-8')).hexdigest(),
                email=body.get('email')
            )
            user.save()
            ret = json.dumps({'message':'user Created '})
            return HTTPResponse(status=200, body=ret)
    except IntegrityError:
        ret = json.dumps({'message':'user already exists'})
        return HTTPResponse(status=500, body=ret)

def generate_token(usr):
    """generates jwt for input user
    """
    token = jwt.encode({"user":usr, "exp":datetime.datetime.utcnow()
                                          + datetime.timedelta(minutes=30)}, KEY)
    return token

@route('/login', method='POST')
def login():
    """POST Login for users
    Takes in a JSON with username and password
    returns a JSON with the username and a jwt
    """
    body = request.json
    try:
        password = md5(body.get('password').encode('utf-8')).hexdigest()
        user = User.get(
            (User.username == body.get('username')) &
            (User.password == password))
        token = generate_token(body.get('username'))
        ret = {"token":token.decode('utf-8'), "username":user.username}
        return HTTPResponse(status=200, body=ret)
    except User.DoesNotExist:
        ret = json.dumps({'message':'Error on login.'})
        return HTTPResponse(status=500, body=ret)

def validate_token(user, tkn):
    """validates inputs
    takes in user and a jwt to validate them
    """
    try:
        decoded = jwt.decode(tkn, KEY)
        if decoded['user'] == user:
            return True
        return False
    except jwt.ExpiredSignatureError:
        return HTTPResponse(status=400, body={"msg":"Validation error."})



@route('/create-note', method='POST')
def save_note():
    """POST to create note
    takes in a JSON with username, jwt, title and content for the notec
    might return error if jwt is not valid or expired
    """
    body = request.json
    user = body.get('username')
    token = body.get('token')
    if not validate_token(user, token):
        return HTTPResponse(status=400, body={"msg":"Validation error."})

    new_token = generate_token(user)
    note_title = body.get('title')
    note_content = body.get('content')
    user_id = (User.get(User.username == user)).id
    new_note = Notes(user=user_id, title=note_title, content=note_content)
    new_note.save()
    ret = {"token":new_token.decode('utf-8'), "username":user}
    return HTTPResponse(status=500, body=ret)

@route('/list-user-notes/<user>/<token>', method="GET")
def get_all_notes(user, token):
    """GET to list notes for user
    takes in parameters from url for user and the jwt
    """
    if not validate_token(user, token):
        return HTTPResponse(status=400, body={"msg":"Validation error."})
    res = []
    user_id = (User.get(User.username == user)).id
    for note in Notes.select():
        if note.user.id == user_id:
            res.append(model_to_dict(note))
    return {'items':res}


create_tables()
run(host='localhost', port=8000)
