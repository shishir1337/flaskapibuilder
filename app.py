from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
import datetime
import os


# initialize Flask app and SQLAlchemy
app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'notes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



# Note model
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.String(50))

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    api_key = db.Column(db.String(100), unique=True)
    api_name = db.Column(db.String(50))



# create tables
with app.app_context():
    db.create_all()


# create a new user
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(
        username=data['username'],
        password=data['password'],
        api_key=str(uuid.uuid4()),
        api_name=data['api_name']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({
        'message': 'New user created!',
        'api_key': new_user.api_key,
        'api_name': new_user.api_name
    })

# get all notes for a specific user
@app.route('/<api_name>/notes', methods=['GET'])
def get_all_notes(api_name):
    api_key = request.headers.get('api_key')
    if not api_key:
        return jsonify({'message': 'Missing API key!'}), 401
    user = User.query.filter_by(api_key=api_key, api_name=api_name).first()
    if not user:
        return jsonify({'message': 'Invalid API key!'}), 401
    notes = Note.query.filter_by(user_id=user.id).all()
    output = []
    for note in notes:
        note_data = {'id': note.id, 'title': note.title, 'content': note.content, 'created_at': note.created_at}
        output.append(note_data)
    return jsonify({'notes': output})


# get a specific note for a specific user
@app.route('/<api_name>/notes/<note_id>', methods=['GET'])
def get_note_by_id(api_name, note_id):
    api_key = request.headers.get('api_key')
    if not api_key:
        return jsonify({'message': 'Missing API key!'}), 401
    user = User.query.filter_by(api_key=api_key).first()
    if not user:
        return jsonify({'message': 'Invalid API key!'}), 401
    note = Note.query.filter_by(id=note_id, user_id=user.id).first()
    if not note:
        return jsonify({'message': 'Note not found!'}), 404
    note_data = {'id': note.id, 'title': note.title, 'content': note.content, 'created_at': note.created_at}
    return jsonify({'note': note_data})


# create a new note for a specific user
@app.route('/<api_name>/notes', methods=['POST'])
def create_note(api_name):
    api_key = request.headers.get('api_key')
    if not api_key:
        return jsonify({'message': 'Missing API key!'}), 401
    user = User.query.filter_by(api_key=api_key).first()
    if not user:
        return jsonify({'message': 'Invalid API key!'}), 401
    data = request.get_json()
    new_note = Note(title=data['title'], content=data['content'], user_id=user.id)
    db.session.add(new_note)
    db.session.commit()
    return jsonify({'message': 'New note created!', 'note_id': new_note.id})

# update an existing note for a specific user
@app.route('/<api_name>/notes/<note_id>', methods=['PUT'])
def update_note_by_id(note_id):
    api_key = request.headers.get('api_key')
    user = User.query.filter_by(api_key=api_key).first()
    if not user:
        return jsonify({'message': 'Invalid API key!'}), 401
    note = Note.query.filter_by(id=note_id, user_id=user.id).first()
    if not note:
        return jsonify({'message': 'Note not found!'}), 404
    data = request.get_json()
    note.title = data.get('title', note.title)
    note.content = data.get('content', note.content)
    db.session.commit()
    return jsonify({'message': 'Note updated!', 'note_id': note.id})


# delete a note for a specific user
@app.route('/<api_name>/notes/<note_id>', methods=['DELETE'])
def delete_note_by_id(note_id):
    api_key = request.headers.get('api_key')
    user = User.query.filter_by(api_key=api_key).first()
    if not user:
        return jsonify({'message': 'Invalid API key!'}), 401
    note = Note.query.filter_by(id=note_id, user_id=user.id).first()
    if not note:
        return jsonify({'message': 'Note not found!'}), 404
    db.session.delete(note)
    db.session.commit()
    return jsonify({'message': 'Note deleted!', 'note_id': note.id})


if __name__ == '__main__':
    app.run(debug=True)
