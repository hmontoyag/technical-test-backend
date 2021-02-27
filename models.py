# Run with "python server.py"
"""
Models and table creation
"""
from peewee import *



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
    token = CharField(null=True)


class Notes(BaseModel):
    """Notes Model
    user is foreign key to User model, Id added by default
    """
    user = ForeignKeyField(User, backref='notes')
    title = CharField()
    content = TextField()


def create_tables():
    """creates tables if not created
    """
    with db:
        db.create_tables([User, Notes])
