def test_create_user(test_client):
    response = test_client.post('/api/create-user', json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 201
    data = response.get_json()
    assert data['status'] == 'user added'

def test_login_success(test_client):
    response = test_client.post('/api/login', json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    data = response.get_json()
    assert "logged in successfully" in data['message']
