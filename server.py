# Run with "python server.py"

from bottle import run, route, template, request
from peewee import *
from playhouse.shortcuts import model_to_dict
# Start your code here, good luck (: ...
db = SqliteDatabase('content.db')

class Notes(Model):
    title = CharField()
    content = TextField()

    class Meta:
        database = db

db.connect()
#db.create_tables([Notes])
def createNote(new_title,new_content):
    new_note = Notes(title=new_title, content=new_content)
    new_note.save()

@route('/hello')
def HelloWorld():
    return "HelloWorld"

@route('/')
@route('/hello/<name>')
def greet(name='Stranger'):
    return template('Hello {{name}}, how are you?', name=name)

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
#test = Notes(title='test1', content='Bueno esta parte deberia ser mas pendeja pa ver si funca.\nse.')
#test.save()
for note in Notes.select():
    print(note.title)
run(host='localhost', port=8000)
