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
from models import User, Notes, create_tables
from token_utilities import generate_token, validate_token, clear_token
# Start your code here, good luck (: ...
db = SqliteDatabase('content.db')


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
                password=md5(body.get('password').encode('utf-8')).hexdigest()
            )
            user.save()
            print(model_to_dict(user))
            ret = json.dumps({'message':'user created'})
            return HTTPResponse(status=200, body=ret)
    except IntegrityError:
        ret = json.dumps({'message':'user already exists'})
        return HTTPResponse(status=500, body=ret)


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
        return HTTPResponse(status=400, body={"message":"Validation error."})
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
        return HTTPResponse(status=500, body={"message":"Validation error."})
    res = []
    user_id = (User.get(User.username == user)).id
    for note in Notes.select():
        if note.user.id == user_id:
            n = model_to_dict(note)
            res.append({"id":n['id'], "title":n['title'],
                        "content":n['content']})
    new_token = generate_token(user)
    body = {"token":new_token.decode('utf-8'), 'items':res}
    return HTTPResponse(status=200, body=body)


@route('/logout', method='POST')
def logout():
    body = request.json
    user = body.get('username')
    clear_token(user)
    return HTTPResponse(status=200)


create_tables()
run(host='localhost', port=8000)
