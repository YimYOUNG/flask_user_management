import pytest
from app.utils.db import create_user, get_user_by_username, get_user_by_email
from werkzeug.security import generate_password_hash, check_password_hash

def get_csrf_token(client, url):
    response = client.get(url)
    import re
    match = re.search(r'name="csrf_token" value="([^"]+)"', response.data.decode('utf-8'))
    if match:
        return match.group(1)
    return ''

def test_register_success(client):
    response = client.post('/auth/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Test1234',
        'confirm_password': 'Test1234',
        'csrf_token': get_csrf_token(client, '/auth/register')
    }, follow_redirects=True)
    assert response.status_code == 200

def test_register_invalid_email(client):
    response = client.post('/auth/register', data={
        'username': 'testuser2',
        'email': 'invalid-email',
        'password': 'Test1234',
        'confirm_password': 'Test1234',
        'csrf_token': get_csrf_token(client, '/auth/register')
    })
    assert response.status_code == 200

def test_register_weak_password(client):
    response = client.post('/auth/register', data={
        'username': 'testuser3',
        'email': 'test3@example.com',
        'password': 'weak',
        'confirm_password': 'weak',
        'csrf_token': get_csrf_token(client, '/auth/register')
    })
    assert response.status_code == 200

def test_register_duplicate_username(client):
    create_user('existinguser', 'existing@example.com', generate_password_hash('Test1234'))
    
    response = client.post('/auth/register', data={
        'username': 'existinguser',
        'email': 'new@example.com',
        'password': 'Test1234',
        'confirm_password': 'Test1234',
        'csrf_token': get_csrf_token(client, '/auth/register')
    })
    assert response.status_code == 200

def test_register_duplicate_email(client):
    create_user('existinguser2', 'existing2@example.com', generate_password_hash('Test1234'))
    
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'existing2@example.com',
        'password': 'Test1234',
        'confirm_password': 'Test1234',
        'csrf_token': get_csrf_token(client, '/auth/register')
    })
    assert response.status_code == 200

def test_login_success(client):
    create_user('logintest', 'login@example.com', generate_password_hash('Test1234'))
    
    response = client.post('/auth/login', data={
        'username': 'logintest',
        'password': 'Test1234',
        'csrf_token': get_csrf_token(client, '/auth/login')
    }, follow_redirects=True)
    assert response.status_code == 200

def test_login_with_email(client):
    create_user('emailtest', 'email@example.com', generate_password_hash('Test1234'))
    
    response = client.post('/auth/login', data={
        'username': 'email@example.com',
        'password': 'Test1234',
        'csrf_token': get_csrf_token(client, '/auth/login')
    }, follow_redirects=True)
    assert response.status_code == 200

def test_login_invalid_credentials(client):
    response = client.post('/auth/login', data={
        'username': 'nonexistent',
        'password': 'wrongpassword',
        'csrf_token': get_csrf_token(client, '/auth/login')
    })
    assert response.status_code == 200

def test_logout(client):
    create_user('logouttest', 'logout@example.com', generate_password_hash('Test1234'))
    
    client.post('/auth/login', data={
        'username': 'logouttest',
        'password': 'Test1234',
        'csrf_token': get_csrf_token(client, '/auth/login')
    })
    
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200

def test_login_already_logged_in(client):
    create_user('alreadytest', 'already@example.com', generate_password_hash('Test1234'))
    
    client.post('/auth/login', data={
        'username': 'alreadytest',
        'password': 'Test1234',
        'csrf_token': get_csrf_token(client, '/auth/login')
    })
    
    response = client.get('/auth/login', follow_redirects=True)
    assert response.status_code == 200

def test_register_already_logged_in(client):
    create_user('regtest', 'reg@example.com', generate_password_hash('Test1234'))
    
    client.post('/auth/login', data={
        'username': 'regtest',
        'password': 'Test1234',
        'csrf_token': get_csrf_token(client, '/auth/login')
    })
    
    response = client.get('/auth/register', follow_redirects=True)
    assert response.status_code == 200
# 在 test_auth.py 末尾添加
def test_login_empty_fields(client):
    response = client.post('/auth/login', data={
        'username': '',
        'password': '',
        'csrf_token': get_csrf_token(client, '/auth/login')
    })
    assert response.status_code == 200

def test_register_password_mismatch(client):
    response = client.post('/auth/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Test1234',
        'confirm_password': 'Different123',
        'csrf_token': get_csrf_token(client, '/auth/register')
    })
    assert response.status_code == 200

def test_register_email_too_long(client):
    long_email = 'a' * 121 + '@example.com'
    response = client.post('/auth/register', data={
        'username': 'testuser',
        'email': long_email,
        'password': 'Test1234',
        'confirm_password': 'Test1234',
        'csrf_token': get_csrf_token(client, '/auth/register')
    })
    assert response.status_code == 200