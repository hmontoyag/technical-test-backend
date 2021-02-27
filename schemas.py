from marshmallow import Schema, fields, validate, ValidationError


class UserSchema(Schema):
    username = fields.Email(
        required=True)
    password = fields.Str(required = True,
                          validate=[validate.Length(min=8,max=40)])
    token = fields.Str()
    class Meta:
        strict = True


class NotesSchema(Schema):
    user = fields.Email(required = True)
    title = fields.Str(required = True,
                        validate=[validate.Length(min=1, max=50)])
    content = fields.Str(required = True,
                         validate=[validate.Length(min=1)])
    class Meta:
        strict = True

user_schema = UserSchema()
notes_schema = NotesSchema()


def validate_user(username, password):
    try:
        data = user_schema.validate({"username":username, "password":password})
        return "OK"
    except ValidationError as err:
        return str(err.messages)

def validate_note(user,title,content):
    try:
        data = notes_schema.validate({"user":user, "title":title,
                                     "content":content})
        return "OK"
    except ValidationError as err:
        return str(err.messages)
