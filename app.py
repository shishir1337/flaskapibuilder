from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
import datetime
import os
from functools import wraps
import jwt



# initialize Flask app and SQLAlchemy go
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

# dashboard
@app.route('/dashboard', methods=['GET'])
def dashboard():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
            # TODO: do something with the user_id to fetch user data from DB or perform some other action
            return jsonify({'message': 'Welcome to your dashboard!'})
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except (jwt.InvalidTokenError, Exception):
            return jsonify({'message': 'Invalid token!'}), 401
    else:
        return jsonify({'message': 'Authorization header is missing!'}), 401

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

# authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated


# login user
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or not data.get('username') or not data.get('password'):
        return make_response('Invalid username or password', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    user = User.query.filter_by(username=data['username']).first()
    if not user or user.password != data['password']:
        return make_response('Invalid username or password', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    token = jwt.encode({'user_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
    return jsonify({'token': token})



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
