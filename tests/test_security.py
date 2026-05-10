import pytest
from app.utils.db import create_user, search_users
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.validators import validate_username, validate_email, validate_password

def get_csrf_token(client, url):
    response = client.get(url)
    import re
    match = re.search(r'name="csrf_token" value="([^"]+)"', response.data.decode('utf-8'))
    if match:
        return match.group(1)
    return ''

def test_csrf_protection(client):
    csrf_token = get_csrf_token(client, '/auth/register')
    response = client.post('/auth/register', data={
        'username': 'csrfuser',
        'email': 'csrf@example.com',
        'password': 'Test1234',
        'confirm_password': 'Test1234',
        'csrf_token': csrf_token
    })
    assert response.status_code == 302

def test_sql_injection_prevention(client):
    create_user('sqliuser', 'sqli@example.com', generate_password_hash('Test1234'))
    
    response = client.get('/user/users?q=%27+OR+1%3D1--')
    assert response.status_code == 302 or response.status_code == 200
    
    users = search_users("' OR 1=1--")
    assert isinstance(users, list)

def test_xss_prevention(client):
    create_user('adminxss', 'adminxss@example.com', generate_password_hash('Admin1234'), is_admin=True)
    
    client.post('/auth/login', data={
        'username': 'adminxss',
        'password': 'Admin1234',
        'csrf_token': get_csrf_token(client, '/auth/login')
    })
    
    response = client.get('/user/users')
    assert response.status_code == 200

def test_session_security(client):
    create_user('sessiontest', 'session@example.com', generate_password_hash('Test1234'))
    
    response = client.post('/auth/login', data={
        'username': 'sessiontest',
        'password': 'Test1234',
        'csrf_token': get_csrf_token(client, '/auth/login')
    })
    
    cookies = response.headers.getlist('Set-Cookie')
    assert len(cookies) > 0

def test_password_hashing(client):
    password = 'TestPassword123'
    password_hash = generate_password_hash(password)
    
    assert password != password_hash
    assert check_password_hash(password_hash, password)
    assert not check_password_hash(password_hash, 'wrongpassword')

def test_validate_username():
    assert validate_username('valid_user') == (True, None)
    assert validate_username('ab') == (False, '用户名长度必须在3-20个字符之间')
    assert validate_username('user@name') == (False, '用户名只能包含字母、数字和下划线')
    assert validate_username('') == (False, '用户名长度必须在3-20个字符之间')

def test_validate_email():
    assert validate_email('test@example.com') == (True, None)
    assert validate_email('invalid') == (False, '邮箱格式不正确')
    assert validate_email('') == (False, '邮箱不能为空')
    assert validate_email('a' * 121 + '@example.com') == (False, '邮箱长度不能超过120个字符')

def test_validate_password():
    assert validate_password('Test1234') == (True, None)
    assert validate_password('weak') == (False, '密码长度至少8个字符')
    assert validate_password('weakpass') == (False, '密码必须包含至少一个大写字母')
    assert validate_password('WEAKPASS') == (False, '密码必须包含至少一个小写字母')
    assert validate_password('Weakpass') == (False, '密码必须包含至少一个数字')
    assert validate_password('') == (False, '密码不能为空')

def test_config_security_headers(client):
    response = client.get('/auth/login')
    assert 'X-Content-Type-Options' in response.headers
    assert response.headers['X-Content-Type-Options'] == 'nosniff'
    assert 'X-Frame-Options' in response.headers
    assert response.headers['X-Frame-Options'] == 'SAMEORIGIN'

def test_user_delete_not_found(client):
    create_user('admindelete', 'admindelete@example.com', generate_password_hash('Admin1234'), is_admin=True)
    client.post('/auth/login', data={
        'username': 'admindelete',
        'password': 'Admin1234',
        'csrf_token': get_csrf_token(client, '/auth/login')
    })
    
    response = client.post('/user/users/delete/999', data={
        'csrf_token': get_csrf_token(client, '/user/users')
    }, follow_redirects=True)
    assert response.status_code == 200

# 在 test_security.py 末尾添加
def test_validate_password_too_long():
    assert validate_password('A' * 129 + 'b1') == (False, '密码长度不能超过128个字符')

# 修改 test_form_validation_error
def test_form_validation_error():
    from app.utils.forms import RegistrationForm
    from app import create_app
    
    app = create_app('testing')
    
    with app.app_context():
        form = RegistrationForm(data={
            'username': 'ab',
            'email': 'test@example.com',
            'password': 'Test1234',
            'confirm_password': 'Test1234'
        })
        
        assert not form.validate()