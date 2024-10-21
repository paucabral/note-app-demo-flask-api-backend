import os
import sys

import pytest

# Append the project path to the system path
current_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(current_dir, ".."))

# pylint: disable=wrong-import-position
from app import app                 # pylint: disable=import-error
from models import db, User, Note   # pylint: disable=import-error
# pylint: enable=wrong-import-position

class TestIntegration:

    @pytest.fixture(autouse=True)
    def setUp(self):
        """Set up the test environment"""
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

        yield

        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def register(self, username, password):
        """Helper function to create user"""
        response = self.client.post(
            "/api/register",
            json={'username': username, 'password': password},
            follow_redirects=True
        )
        assert response.status_code == 201

        # After registration, retrieve and store the user for later tests
        with app.app_context():
            self.test_user = User.query.filter_by(username=username).first()

    def login(self, username, password):
        """Helper function to log in and get the JWT token"""
        response = self.client.post(
            "/api/login",
            json={'username': username, 'password': password},
        )
        assert response.status_code == 200
        data = response.get_json()
        return data['access_token']

    def logout(self, token):
        response = self.client.get(
            "/api/logout",
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        return data['msg']
    
    def test_login_logout(self):
        """Test the login and logout process"""
        self.register(os.getenv("TEST_USER"), os.getenv("TEST_PASSWORD"))
        token = self.login(os.getenv("TEST_USER"), os.getenv("TEST_PASSWORD"))
        assert token is not None

        self.logout(token)

    def test_register_login(self):
        """Test the registration and login process, and token retrieval"""
        self.register(os.getenv("TEST_USER"), os.getenv("TEST_PASSWORD"))
        token = self.login(os.getenv("TEST_USER"), os.getenv("TEST_PASSWORD"))
        assert token is not None

    def test_create_note(self):
        """Test creating a note"""
        self.register(os.getenv("TEST_USER"), os.getenv("TEST_PASSWORD"))
        token = self.login(os.getenv("TEST_USER"), os.getenv("TEST_PASSWORD"))

        response = self.client.post(
            "/api/notes",
            json={
                'title': 'New Note',
                'content': 'A test note'
            },
            headers={'Authorization': f'Bearer {token}'},
            follow_redirects=True
        )
        assert response.status_code == 201

        # Check if the note was added to the database
        with app.app_context():
            note = Note.query.filter_by(title='New Note').first()
            assert note is not None

    def test_read_notes(self):
        """Test reading notes"""
        self.register(os.getenv("TEST_USER"), os.getenv("TEST_PASSWORD"))
        token = self.login(os.getenv("TEST_USER"), os.getenv("TEST_PASSWORD"))

        # Create a note first
        self.client.post(
            "/api/notes",
            json={
                'title': 'New Note',
                'content': 'A test note'
            },
            headers={'Authorization': f'Bearer {token}'},
            follow_redirects=True
        )

        response = self.client.get(
            "/api/notes",
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
        assert b"New Note" in response.data

    def test_update_note(self):
        """Test updating a note"""
        self.register(os.getenv("TEST_USER"), os.getenv("TEST_PASSWORD"))
        token = self.login(os.getenv("TEST_USER"), os.getenv("TEST_PASSWORD"))

        # Create a note
        with app.app_context():
            note = Note(title="Old Title", content="Old Content", user_id=self.test_user.id)
            db.session.add(note)
            db.session.commit()

        # Query the note again inside an active session to ensure it's bound
        with app.app_context():
            note = Note.query.filter_by(title="Old Title").first()

        response = self.client.put(
            f"/api/notes/{note.id}",
            json={
                'title': 'Updated Title',
                'content': 'Updated Content'
            },
            headers={'Authorization': f'Bearer {token}'},
            follow_redirects=True
        )
        assert response.status_code == 200

        # Verify that the update was successful
        with app.app_context():
            updated_note = db.session.get(Note, note.id)
            assert updated_note.title == 'Updated Title'

    def test_delete_note(self):
        """Test deleting a note"""
        self.register(os.getenv("TEST_USER"), os.getenv("TEST_PASSWORD"))
        token = self.login(os.getenv("TEST_USER"), os.getenv("TEST_PASSWORD"))

        # Create a note
        with app.app_context():
            note = Note(title="Delete Me", content="To be deleted", user_id=self.test_user.id)
            db.session.add(note)
            db.session.commit()

        # Query the note again inside an active session to ensure it's bound
        with app.app_context():
            note = Note.query.filter_by(title="Delete Me").first()

        # Delete the note
        response = self.client.delete(
            f"/api/notes/{note.id}/delete",
            headers={'Authorization': f'Bearer {token}'},
            follow_redirects=True
        )
        assert response.status_code == 200

        # Verify that the note was deleted
        with app.app_context():
            deleted_note = db.session.get(Note, note.id)
            assert deleted_note is None

if __name__ == '__main__':
    pytest.main()