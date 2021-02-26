# Run with "python server.py"
import json
from bottle import run, route, template, request, hook, response, HTTPResponse
from peewee import *
from hashlib import md5
from playhouse.shortcuts import model_to_dict
import jwt
import datetime
# Start your code here, good luck (: ...
db = SqliteDatabase('content.db')
KEY = 'MIIBVAIBADANBgkqhkiG9w0BAQEFAASCAT4wggE6AgEAAkEAkgDUAAjZUpWw9z'
class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    username = CharField(unique=True)
    password = CharField()
    email = CharField()

class Dummy(BaseModel):
    name = CharField()

class Notes(BaseModel):
    user = ForeignKeyField(User, backref='notes')
    title = CharField()
    content = TextField()

@hook('before_request')
def before_request():
    db.connect()

@hook('after_request')
def after_request():
    db.close()
    return

def create_tables():
    with db:
        db.create_tables([User,Notes, Dummy])

@route('/create-dummy', method='POST')
def createDummy():
    body = request.json
    n = body.get('name')
    dm = Dummy(name=n)
    dm.save()
    ret = json.dumps({'message':'Created ' + n})
    return HTTPResponse(status = 200, body=ret )
@route('/get-dummies', method='GET')
def getDummies():
    res = []
    for d in Dummy.select():
        res.append(model_to_dict(d))
    return {'dummies':res}

@route('/create-user', method='POST')
def create_user():
    try:
        body = request.json
        with db.atomic():
            user = User.create(
                username = body.get('username'),
                password = md5(body.get('password').encode('utf-8')).hexdigest(),
                email = body.get('email')
            )
            user.save()
            ret = json.dumps({'message':'user Created '})
            return HTTPResponse(status = 200, body=ret )
    except IntegrityError:
        ret = json.dumps({'message':'user already exists'})
        return HTTPResponse(status = 500, body=ret )

def generate_token(usr):
    token = jwt.encode({"user":usr, "exp":datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},KEY)
    return token

@route('/login', method='POST')
def login():
    body = request.json
    try:
        pw = md5(body.get('password').encode('utf-8')).hexdigest()
        user = User.get(
            (User.username == body.get('username')) &
            (User.password == pw))
        token = generate_token(body.get('username'))
        ret = {"token":token.decode('utf-8'), "username":body.get('username')}
        return HTTPResponse(status=200,body=ret)
    except User.DoesNotExist:
        ret = json.dumps({'message':'Error on login.'})
        return HTTPResponse(status = 500, body=ret)

def validate_token(user,tkn):
    try:
        decoded = jwt.decode(tkn, KEY)
        if decoded['user'] == user:
            return True
        else:
            return False
    except jwt.ExpiredSignatureError:
        return HTTPResponse(status = 400, body={"msg":"Validation error."})



@route('/create-note', method='POST')
def save_note():
    body = request.json
    user = body.get('username')
    token = body.get('token')
    if not validate_token(user,token):
        return HTTPResponse(status=400,body={"msg":"Validation error."})

    new_token = generate_token(user)
    note_title = body.get('title')
    note_content = body.get('content')
    id = (User.get(User.username==user)).id
    new_note = Notes(user=id,title=note_title, content = note_content)
    new_note.save()
    ret = {"token":new_token.decode('utf-8'), "username":user}
    return HTTPResponse(status = 500, body=ret)

@route('/list-user-notes/<user>/<token>', method="GET")
def get_all_notes(user,token):
    if not validate_token(user,token):
        return HTTPResponse(status=400,body={"msg":"Validation error."})
    res = []
    id = (User.get(User.username==user)).id
    for note in Notes.select():
        if note.user.id == id:
            res.append(model_to_dict(note))
    return {'items':res}


create_tables()
run(host='localhost', port=8000)
