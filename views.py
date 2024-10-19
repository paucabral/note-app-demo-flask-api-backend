
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from flask_migrate import Migrate

from models import db, User, Note
from schemas import ma, note_schema, notes_schema

app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)
ma.init_app(app)
migrate = Migrate(app, db)

jwt = JWTManager(app)

# Register
@app.route('/api/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        response = {
            "error": "Invalid username or password"
        }

        return jsonify(response), 400

    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        response = {
            "error": "Username already exists"
        }

        return jsonify(response), 400

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    response = {
        "message": "User registered successfully."
    }

    return jsonify(response), 201

# Login
@app.route('/api/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        response = {
            "error": "Invalid username or password"
        }

        return jsonify(response), 401
    
    access_token = create_access_token(identity=user.id)
    response = {
        "access_token": access_token
    }

    return jsonify(response), 200

# Create a new note
@app.route('/api/notes', methods=['POST'])
@jwt_required()
def create_note():
    try:
        data = request.json
        user_id = get_jwt_identity()
        note = Note(user_id=user_id, title=data["title"], content=data["content"])
        db.session.add(note)
        db.session.commit()
        
        response = {
            "message": f"Note added with id: {note.id}"
        }

        return jsonify(response), 201
    except (KeyError, TypeError):
        response = {
            "error": "Invalid Data"
        }
        
        return jsonify(response), 400

@app.route('/api/notes', methods=['GET'])
@jwt_required()
def get_notes():
    user_id = get_jwt_identity()
    all_notes = Note.query.filter_by(user_id=user_id).all()
    response = notes_schema.dump(all_notes)
    return jsonify(response), 200

@app.route('/api/notes/<int:note_id>', methods=['GET'])
@jwt_required()
def get_note(note_id):
    try:
        user_id = get_jwt_identity()
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()
        if note:
            response = note_schema.dump(note)
            return jsonify(response), 200
        else:
            response = {
                "error": "Note not found"
            }
            return jsonify(response), 404
    except (ValueError, TypeError):
        response = {
            "error": "Invalid note ID"
        }

        return jsonify(response), 400

@app.route('/api/notes/<int:note_id>', methods=['PUT'])
@jwt_required()
def update_note(note_id):
    try:
        user_id = get_jwt_identity()
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()
        if note:
            data = request.get_json()
            note.title = data['title']
            note.content = data['content']
            db.session.commit()

            response = note_schema.dump(note)
            return jsonify(response), 200
        else:
            response = {
                "error": "Note not found"
            }
            return jsonify(response), 404
    except (ValueError, TypeError):
        response = {
            "error": "Invalid data"
        }
        return jsonify(response), 400

@app.route('/api/notes/<int:note_id>/delete', methods=['DELETE'])
@jwt_required()
def delete_note(note_id):
    try:
        user_id = get_jwt_identity()
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()
        if note:
            db.session.delete(note)
            db.session.commit()
            response = {
                "message": "Note deleted"
            }
            return jsonify(response), 200
        else:
            response = {
                "error": "Note not found"
            }
            return jsonify(response), 404
    except (ValueError, TypeError):
        response = {
            "error": "Invalid note ID"
        }
        return jsonify(response), 400