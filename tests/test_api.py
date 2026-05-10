import json
import pytest
from app.utils.db import create_user, get_user_by_id
from werkzeug.security import generate_password_hash

def login_as_admin(client):
    create_user('apiadmintest', 'apiadmin@example.com', generate_password_hash('Admin1234'), is_admin=True)
    client.post('/auth/login', data={
        'username': 'apiadmintest',
        'password': 'Admin1234',
        'csrf_token': get_csrf_token(client, '/auth/login')
    })

def login_as_user(client):
    create_user('apiusertest', 'apiuser@example.com', generate_password_hash('User1234'), is_admin=False)
    client.post('/auth/login', data={
        'username': 'apiusertest',
        'password': 'User1234',
        'csrf_token': get_csrf_token(client, '/auth/login')
    })

def get_csrf_token(client, url):
    response = client.get(url)
    import re
    match = re.search(r'name="csrf_token" value="([^"]+)"', response.data.decode('utf-8'))
    if match:
        return match.group(1)
    return ''

def test_api_users_list(client):
    login_as_admin(client)
    response = client.get('/api/users')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'users' in data
    assert 'total' in data

def test_api_users_list_pagination(client):
    login_as_admin(client)
    for i in range(15):
        create_user(f'pageduser{i}', f'paged{i}@example.com', generate_password_hash('Test1234'))
    
    response = client.get('/api/users?page=2&per_page=5')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['page'] == 2
    assert data['per_page'] == 5

def test_api_user_get(client):
    user_id = create_user('user1', 'user1@example.com', generate_password_hash('Test1234'))
    client.post('/auth/login', data={
        'username': 'user1',
        'password': 'Test1234',
        'csrf_token': get_csrf_token(client, '/auth/login')
    })
    
    response = client.get(f'/api/users/{user_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['username'] == 'user1'

def test_api_user_get_not_found(client):
    login_as_admin(client)
    response = client.get('/api/users/999')
    assert response.status_code == 404

def test_api_user_create(client):
    response = client.post('/api/users', 
        json={
            'username': 'apicreatetest',
            'email': 'apicreate@example.com',
            'password': 'Test1234'
        },
        content_type='application/json'
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['username'] == 'apicreatetest'

def test_api_user_create_invalid(client):
    response = client.post('/api/users',
        json={
            'username': 'ab',
            'email': 'invalid',
            'password': 'weak'
        },
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_api_user_create_duplicate(client):
    create_user('dupuser123', 'dup123@example.com', generate_password_hash('Test1234'))
    
    response = client.post('/api/users',
        json={
            'username': 'dupuser123',
            'email': 'newemail@example.com',
            'password': 'Test1234'
        },
        content_type='application/json'
    )
    assert response.status_code == 409

def test_api_user_update(client):
    user_id = create_user('apiupdatetest', 'apiupdate@example.com', generate_password_hash('Test1234'))
    login_as_admin(client)
    
    response = client.put(f'/api/users/{user_id}',
        json={
            'username': 'apiupdated',
            'email': 'apiupdated@example.com'
        },
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['username'] == 'apiupdated'

def test_api_user_update_not_found(client):
    login_as_admin(client)
    response = client.put('/api/users/999',
        json={'username': 'test'},
        content_type='application/json'
    )
    assert response.status_code == 404

def test_api_user_delete(client):
    user_id = create_user('apideletetest', 'apidelete@example.com', generate_password_hash('Test1234'))
    login_as_admin(client)
    
    response = client.delete(f'/api/users/{user_id}')
    assert response.status_code == 200

def test_api_user_delete_self(client):
    admin_id = create_user('admindelete', 'admindelete@example.com', generate_password_hash('Admin1234'), is_admin=True)
    client.post('/auth/login', data={
        'username': 'admindelete',
        'password': 'Admin1234',
        'csrf_token': get_csrf_token(client, '/auth/login')
    })
    
    response = client.delete(f'/api/users/{admin_id}')
    assert response.status_code == 400

def test_api_login(client):
    create_user('apilogintest', 'apilogin@example.com', generate_password_hash('Test1234'))
    
    response = client.post('/api/auth/login',
        json={
            'username': 'apilogintest',
            'password': 'Test1234'
        },
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'user' in data

def test_api_login_invalid(client):
    response = client.post('/api/auth/login',
        json={
            'username': 'wrong',
            'password': 'wrong'
        },
        content_type='application/json'
    )
    assert response.status_code == 401

def test_api_login_empty(client):
    response = client.post('/api/auth/login',
        json={},
        content_type='application/json'
    )
    assert response.status_code == 400

def test_api_logout(client):
    response = client.post('/api/auth/logout', json={}, content_type='application/json')
    assert response.status_code == 200

def test_api_register(client):
    response = client.post('/api/auth/register',
        json={
            'username': 'apiregtest',
            'email': 'apireg@example.com',
            'password': 'Test1234'
        },
        content_type='application/json'
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'user' in data

def test_api_unauthorized_access(client):
    response = client.get('/api/users')
    assert response.status_code == 401

def test_api_no_data(client):
    response = client.post('/api/users', data='', content_type='application/json')
    assert response.status_code == 400

def test_api_user_access_other(client):
    user1_id = create_user('user1', 'user1@example.com', generate_password_hash('Test1234'))
    create_user('user2', 'user2@example.com', generate_password_hash('Test1234'))
    
    client.post('/auth/login', data={
        'username': 'user2',
        'password': 'Test1234',
        'csrf_token': get_csrf_token(client, '/auth/login')
    })
    
    response = client.get(f'/api/users/{user1_id}')
    assert response.status_code == 403
# 在 test_api.py 末尾添加
def test_api_user_update_password(client):
    user_id = create_user('pwupdate', 'pwupdate@example.com', generate_password_hash('Test1234'))
    login_as_admin(client)
    
    response = client.put(f'/api/users/{user_id}',
        json={'password': 'NewPass123'},
        content_type='application/json'
    )
    assert response.status_code == 200

# 修改 test_api_user_update_email_exists
def test_api_user_update_email_exists(client):
    import uuid
    unique_suffix = str(uuid.uuid4())[:8]
    create_user(f'existuser_{unique_suffix}', f'exist_{unique_suffix}@example.com', generate_password_hash('Test1234'))
    user_id = create_user(f'updateuser_{unique_suffix}', f'update_{unique_suffix}@example.com', generate_password_hash('Test1234'))
    login_as_admin(client)
    
    response = client.put(f'/api/users/{user_id}',
        json={'email': f'exist_{unique_suffix}@example.com'},
        content_type='application/json'
    )
    assert response.status_code == 409

# 修改 test_api_user_update_username_exists
def test_api_user_update_username_exists(client):
    import uuid
    unique_suffix = str(uuid.uuid4())[:8]
    create_user(f'existname_{unique_suffix}', f'existname_{unique_suffix}@example.com', generate_password_hash('Test1234'))
    user_id = create_user(f'updateuser2_{unique_suffix}', f'update2_{unique_suffix}@example.com', generate_password_hash('Test1234'))
    login_as_admin(client)
    
    response = client.put(f'/api/users/{user_id}',
        json={'username': f'existname_{unique_suffix}'},
        content_type='application/json'
    )
    assert response.status_code == 409

def test_api_user_update_invalid_email(client):
    user_id = create_user('invalidemail', 'invalid@example.com', generate_password_hash('Test1234'))
    login_as_admin(client)
    
    response = client.put(f'/api/users/{user_id}',
        json={'email': 'invalid'},
        content_type='application/json'
    )
    assert response.status_code == 400

def test_api_user_update_invalid_username(client):
    user_id = create_user('validuser', 'valid@example.com', generate_password_hash('Test1234'))
    login_as_admin(client)
    
    response = client.put(f'/api/users/{user_id}',
        json={'username': 'ab'},
        content_type='application/json'
    )
    assert response.status_code == 400

def test_api_user_update_admin(client):
    user_id = create_user('adminupdate', 'adminupdate@example.com', generate_password_hash('Test1234'))
    login_as_admin(client)
    
    response = client.put(f'/api/users/{user_id}',
        json={'is_admin': True},
        content_type='application/json'
    )
    assert response.status_code == 200

def test_api_user_update_admin_only(client):
    user_id = create_user('reguser', 'reg@example.com', generate_password_hash('Test1234'))
    login_as_user(client)
    
    response = client.put(f'/api/users/{user_id}',
        json={'username': 'newname'},
        content_type='application/json'
    )
    assert response.status_code == 403

def test_api_users_list_empty(client):
    login_as_admin(client)
    response = client.get('/api/users')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total'] >= 0

def test_api_get_user_unauthorized(client):
    user_id = create_user('unauthuser', 'unauth@example.com', generate_password_hash('Test1234'))
    response = client.get(f'/api/users/{user_id}')
    assert response.status_code == 401

def test_api_users_search(client):
    login_as_admin(client)
    create_user('searchtarget', 'search@example.com', generate_password_hash('Test1234'))
    response = client.get('/api/users?q=searchtarget')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total'] >= 1

def test_api_create_user_empty_json(client):
    login_as_admin(client)
    response = client.post('/api/users', json={}, content_type='application/json')
    assert response.status_code == 400

def test_api_create_user_invalid_email_only(client):
    login_as_admin(client)
    response = client.post('/api/users', json={
        'username': 'validuser123',
        'email': 'invalid',
        'password': 'Test1234'
    }, content_type='application/json')
    assert response.status_code == 400

def test_api_create_user_invalid_password(client):
    login_as_admin(client)
    response = client.post('/api/users', json={
        'username': 'validuser456',
        'email': 'valid@example.com',
        'password': 'weak'
    }, content_type='application/json')
    assert response.status_code == 400

def test_api_create_user_duplicate_email(client):
    create_user('firstuser', 'dupemail@example.com', generate_password_hash('Test1234'))
    login_as_admin(client)
    response = client.post('/api/users', json={
        'username': 'seconduser',
        'email': 'dupemail@example.com',
        'password': 'Test1234'
    }, content_type='application/json')
    assert response.status_code == 409

def test_api_update_user_empty_json(client):
    user_id = create_user('updateempty', 'updateempty@example.com', generate_password_hash('Test1234'))
    login_as_admin(client)
    response = client.put(f'/api/users/{user_id}', json={}, content_type='application/json')
    assert response.status_code == 400

def test_api_delete_user_not_found(client):
    login_as_admin(client)
    response = client.delete('/api/users/999')
    assert response.status_code == 404

def test_api_login_empty_fields(client):
    response = client.post('/api/auth/login', json={
        'username': '',
        'password': ''
    }, content_type='application/json')
    assert response.status_code == 400

def test_api_register_empty_json(client):
    response = client.post('/api/auth/register', json={}, content_type='application/json')
    assert response.status_code == 400

def test_api_register_invalid_username(client):
    response = client.post('/api/auth/register', json={
        'username': 'ab',
        'email': 'test@example.com',
        'password': 'Test1234'
    }, content_type='application/json')
    assert response.status_code == 400

def test_api_register_invalid_email(client):
    response = client.post('/api/auth/register', json={
        'username': 'validuser',
        'email': 'invalid',
        'password': 'Test1234'
    }, content_type='application/json')
    assert response.status_code == 400

def test_api_register_invalid_password(client):
    response = client.post('/api/auth/register', json={
        'username': 'validuser',
        'email': 'valid@example.com',
        'password': 'weak'
    }, content_type='application/json')
    assert response.status_code == 400

def test_api_register_duplicate_username(client):
    create_user('dupuser', 'dupuser@example.com', generate_password_hash('Test1234'))
    response = client.post('/api/auth/register', json={
        'username': 'dupuser',
        'email': 'new@example.com',
        'password': 'Test1234'
    }, content_type='application/json')
    assert response.status_code == 409

def test_api_register_duplicate_email(client):
    create_user('someuser', 'dupemail@example.com', generate_password_hash('Test1234'))
    response = client.post('/api/auth/register', json={
        'username': 'anotheruser',
        'email': 'dupemail@example.com',
        'password': 'Test1234'
    }, content_type='application/json')
    assert response.status_code == 409