import pytest
from app.utils.db import create_user, get_user_by_username
from werkzeug.security import generate_password_hash

def login_as_admin(client):
    create_user('admintest', 'admin@example.com', generate_password_hash('Admin1234'), is_admin=True)
    client.post('/auth/login', data={
        'username': 'admintest',
        'password': 'Admin1234',
        'csrf_token': get_csrf_token(client, '/auth/login')
    })

def login_as_user(client):
    create_user('usertest', 'user@example.com', generate_password_hash('User1234'), is_admin=False)
    client.post('/auth/login', data={
        'username': 'usertest',
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

def test_user_list_admin(client):
    login_as_admin(client)
    response = client.get('/user/users')
    assert response.status_code == 200

def test_user_list_non_admin(client):
    login_as_user(client)
    response = client.get('/user/users')
    assert response.status_code == 302

def test_user_update(client):
    user_id = create_user('updatetest', 'update@example.com', generate_password_hash('Test1234'))
    login_as_admin(client)
    
    response = client.post(f'/user/users/edit/{user_id}', data={
        'username': 'updateduser',
        'email': 'updated@example.com',
        'is_admin': False,
        'is_active': True,
        'csrf_token': get_csrf_token(client, f'/user/users/edit/{user_id}')
    }, follow_redirects=True)
    assert response.status_code == 200

def test_user_update_invalid_email(client):
    user_id = create_user('updateinvalid', 'updateinvalid@example.com', generate_password_hash('Test1234'))
    login_as_admin(client)
    
    response = client.post(f'/user/users/edit/{user_id}', data={
        'username': 'updateduser',
        'email': 'invalid-email',
        'is_admin': False,
        'is_active': True,
        'csrf_token': get_csrf_token(client, f'/user/users/edit/{user_id}')
    })
    assert response.status_code == 200

def test_user_delete_self_direct(client):
    login_as_admin(client)
    from app.utils.db import get_user_by_username
    admin = get_user_by_username('admintest')
    response = client.post(f'/user/users/delete/{admin["id"]}', data={
        'csrf_token': get_csrf_token(client, '/user/users')
    }, follow_redirects=True)
    assert response.status_code == 200

def test_db_rollback(client):
    from app.utils.db import get_db
    import pytest
    with pytest.raises(Exception):
        with get_db() as conn:
            conn.execute("INSERT INTO users (username, email, password_hash) VALUES ('rollback_test', 'rollback@test.com', 'hash')")
            conn.commit()
            raise RuntimeError("force rollback")

def test_user_delete(client):
    user_id = create_user('deletetest', 'delete@example.com', generate_password_hash('Test1234'))
    login_as_admin(client)
    
    response = client.post(f'/user/users/delete/{user_id}', data={
        'csrf_token': get_csrf_token(client, f'/user/users')
    }, follow_redirects=True)
    assert response.status_code == 200

def test_user_delete_self(client):
    create_user('admintest', 'admin@example.com', generate_password_hash('Admin1234'), is_admin=True)
    client.post('/auth/login', data={
        'username': 'admintest',
        'password': 'Admin1234',
        'csrf_token': get_csrf_token(client, '/auth/login')
    })
    
    response = client.get('/user/users')
    import re
    match = re.search(r'/user/users/delete/(\d+)', response.data.decode('utf-8'))
    if match:
        admin_id = match.group(1)
        response = client.post(f'/user/users/delete/{admin_id}', data={
            'csrf_token': get_csrf_token(client, '/user/users')
        }, follow_redirects=True)
        assert response.status_code == 200

def test_user_search(client):
    create_user('searchuser1', 'search1@example.com', generate_password_hash('Test1234'))
    create_user('searchuser2', 'search2@example.com', generate_password_hash('Test1234'))
    login_as_admin(client)
    
    response = client.get('/user/users?q=searchuser1')
    assert response.status_code == 200

def test_user_search_empty(client):
    login_as_admin(client)
    response = client.get('/user/users?q=nonexistentuser')
    assert response.status_code == 200

def test_dashboard_access(client):
    login_as_user(client)
    response = client.get('/user/dashboard')
    assert response.status_code == 200

def test_dashboard_unauthenticated(client):
    response = client.get('/user/dashboard')
    assert response.status_code == 302

def test_edit_user_not_found(client):
    login_as_admin(client)
    response = client.get('/user/users/edit/999')
    assert response.status_code == 302

def test_edit_user_get(client):
    user_id = create_user('edittest', 'edit@example.com', generate_password_hash('Test1234'))
    login_as_admin(client)
    response = client.get(f'/user/users/edit/{user_id}')
    assert response.status_code == 200

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 302

def test_index_authenticated(client):
    create_user('indextest', 'index@example.com', generate_password_hash('Test1234'))
    client.post('/auth/login', data={
        'username': 'indextest',
        'password': 'Test1234',
        'csrf_token': get_csrf_token(client, '/auth/login')
    })
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
# 在 test_user.py 末尾添加
def test_user_update_password_change(client):
    user_id = create_user('pwchangetest', 'pwchange@example.com', generate_password_hash('Test1234'))
    login_as_admin(client)
    
    response = client.post(f'/user/users/edit/{user_id}', data={
        'username': 'pwchangetest',
        'email': 'pwchange@example.com',
        'password': 'NewPass123',
        'confirm_password': 'NewPass123',
        'is_admin': False,
        'is_active': True,
        'csrf_token': get_csrf_token(client, f'/user/users/edit/{user_id}')
    }, follow_redirects=True)
    assert response.status_code == 200

def test_user_search_pagination(client):
    for i in range(10):
        create_user(f'searchuser{i}', f'search{i}@example.com', generate_password_hash('Test1234'))
    login_as_admin(client)
    
    response = client.get('/user/users?q=search&page=1&per_page=5')
    assert response.status_code == 200

def test_user_update_invalid_username(client):
    user_id = create_user('validuser', 'valid@example.com', generate_password_hash('Test1234'))
    login_as_admin(client)
    
    response = client.post(f'/user/users/edit/{user_id}', data={
        'username': 'ab',
        'email': 'valid@example.com',
        'is_admin': False,
        'is_active': True,
        'csrf_token': get_csrf_token(client, f'/user/users/edit/{user_id}')
    })
    assert response.status_code == 200

def test_user_update_invalid_username_char(client):
    user_id = create_user('validuser2', 'valid2@example.com', generate_password_hash('Test1234'))
    login_as_admin(client)
    
    response = client.post(f'/user/users/edit/{user_id}', data={
        'username': 'user@name!',
        'email': 'valid2@example.com',
        'is_admin': False,
        'is_active': True,
        'csrf_token': get_csrf_token(client, f'/user/users/edit/{user_id}')
    })
    assert response.status_code == 200

def test_user_update_invalid_email_format(client):
    user_id = create_user('validuser3', 'valid3@example.com', generate_password_hash('Test1234'))
    login_as_admin(client)
    
    response = client.post(f'/user/users/edit/{user_id}', data={
        'username': 'validuser3',
        'email': 'test@a.b',
        'is_admin': False,
        'is_active': True,
        'csrf_token': get_csrf_token(client, f'/user/users/edit/{user_id}')
    })
    assert response.status_code == 200