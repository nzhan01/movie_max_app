import pytest
from models.user_model import Users
from db.models import db

def test_create_user(test_client):
    response = test_client.post('/api/create-user', json={
        "username": "testuser",
        "password": "testpass"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['status'] == 'user added'
    assert data['username'] == 'testuser'

def test_create_user_duplicate(test_client):
    # Attempt to create the same user again
    response = test_client.post('/api/create-user', json={
        "username": "testuser",
        "password": "testpass2"
    })
    assert response.status_code == 500  # or 400 depending on your error handling
    data = response.get_json()
    assert 'already exists' in data['error']

def test_login_success(test_client):
    # Login with correct credentials
    response = test_client.post('/api/login', json={
        "username": "testuser",
        "password": "testpass"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert "logged in successfully" in data['message']

def test_login_failure(test_client):
    # Login with incorrect password
    response = test_client.post('/api/login', json={
        "username": "testuser",
        "password": "wrongpass"
    })
    assert response.status_code == 401
    data = response.get_json()
    assert "Invalid username or password" in data['error']
