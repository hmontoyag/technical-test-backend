'''
JWT related operations to auth users and maintain sessions
'''
import datetime

import jwt
from peewee import *
from playhouse.shortcuts import model_to_dict
from models import User
KEY = 'MIIBVAIBADANBgkqhkiG9w0BAQEFAASCAT4wggE6AgEAAkEAkgDUAAjZUpWw9z'

def generate_token(usr):
    """generates jwt for input user
    """
    token = jwt.encode({"user":usr, "exp":datetime.datetime.utcnow()
                                          + datetime.timedelta(minutes=30)}, KEY)
    user = User.update(token=token).where(User.username == usr)
    user.execute()
    return token

def validate_token(user, tkn):
    """validates inputs
    takes in user and a jwt to validate them
    """
    try:
        decoded = jwt.decode(tkn, KEY)
        if decoded['user'] == user:
            stored_token = User.get(User.username == user).token
            if stored_token == tkn:
                return True
        return False
    except jwt.ExpiredSignatureError:
        return HTTPResponse(status=400, body={"msg":"Validation error."})

def clear_token(user):
    """Clears the jwt from db
    called when user logs out
    """
    query = User.update(token='').where(User.username == user)
    query.execute()
    usr = User.get(User.username==user)
    print(model_to_dict(usr))
