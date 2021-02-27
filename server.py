# Run with "python server.py"
"""
Starts and keeps the server running. Handles requests.
"""

import json
from hashlib import md5


from bottle import run, route, request, hook, HTTPResponse
from peewee import *
from playhouse.shortcuts import model_to_dict
from models import User, Notes, create_tables
from token_utilities import generate_token, validate_token, clear_token
from schemas import validate_user, validate_note
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
    body = request.json
    username = body.get('username')
    password = body.get('password')
    validation = validate_user(username, password)
    password = md5(password.encode('utf-8')).hexdigest()
    if validation != "OK":
        return HTTPResponse(status=500, body={"message":validation})
    try:
        with db.atomic():
            user = User.create(username=username, password=password)
            user.save()
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
        ret = {"token":token.decode('utf-8'), "user_id":user.id}
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
    user_id = body.get('user_id')
    token = body.get('token')
    user = User.get(User.id == user_id).username
    if not validate_token(user, token):
        return HTTPResponse(status=400, body={"message":"Validation error."})
    note_title = body.get('title')
    note_content = body.get('content')
    validation = validate_note(user, note_title, note_content)
    if validation != "OK":
        return HTTPResponse(status=500, body={"message":validation})
    new_note = Notes(user=user_id, title=note_title, content=note_content)
    new_note.save()
    new_token = generate_token(user)
    ret = {"token":new_token.decode('utf-8'), "user_id":user_id}
    return HTTPResponse(status=500, body=ret)

@route('/list-user-notes/<user_id>/<token>', method="GET")
def get_all_notes(user_id, token):
    """GET to list notes for user
    takes in parameters from url for user and the jwt
    """
    user = User.get(User.id == user_id).username
    if not validate_token(user, token):
        return HTTPResponse(status=500, body={"message":"Validation error."})
    res = []
    for note in Notes.select():
        if note.user.id == user_id:
            new_note = model_to_dict(note)
            res.append({"id":new_note['id'], "title":new_note['title'],
                        "content":new_note['content']})
    new_token = generate_token(user)
    body = {"token":new_token.decode('utf-8'), 'items':res}
    return HTTPResponse(status=200, body=body)


@route('/logout', method='POST')
def logout():
    """POST for user logout
    removes jwt in db preventing further user interaction until login
    """
    body = request.json
    user_id = body.get('user_id')
    user = User.get(User.id == user_id).username
    clear_token(user)
    return HTTPResponse(status=200)


create_tables()
run(host='localhost', port=8000)
