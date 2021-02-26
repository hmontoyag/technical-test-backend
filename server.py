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


@route('/login', method='POST')
def login():
    body = request.json
    try:
        pw = md5(body.get('password').encode('utf-8')).hexdigest()
        user = User.get(
            (User.username == body.get('username')) &
            (User.password == pw))
        ret = json.dumps({'message':'logged in as ' + body.get('username')})
        return HTTPResponse(status=200,body=ret)
    except User.DoesNotExist:
        ret = json.dumps({'message':'Error on login.'})
        return HTTPResponse(status = 500, body=ret)


@route('/savenote', method='POST')
def save_note():
    body = request.json
    note_title = body.get('title')
    note_content = body.get('content')
    new_note = Notes(title=note_title, content = note_content)
    new_note.save()
    return

@route('/allnotes')
def get_all_notes():
    res = []
    for note in Notes.select():
        res.append(model_to_dict(note))
    return {'items':res}

create_tables()
run(host='localhost', port=8000)
