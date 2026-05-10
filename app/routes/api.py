from flask import Blueprint, jsonify, request, session
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.db import (
    get_all_users, get_user_by_id, get_user_by_username, 
    get_user_by_email, create_user, update_user, delete_user, search_users
)
from app.utils.validators import validate_username, validate_email, validate_password

bp = Blueprint('api', __name__, url_prefix='/api')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        if not session.get('is_admin'):
            return jsonify({'error': '需要管理员权限'}), 403
        return f(*args, **kwargs)
    return decorated_function

def serialize_user(user):
    return {
        'id': user['id'],
        'username': user['username'],
        'email': user['email'],
        'is_admin': bool(user['is_admin']),
        'is_active': bool(user['is_active']),
        'created_at': user['created_at'],
        'last_login': user['last_login']
    }

@bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('q', '')
    
    if search:
        users = search_users(search)
    else:
        users = get_all_users()
    
    total = len(users)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_users = users[start:end]
    
    return jsonify({
        'users': [serialize_user(user) for user in paginated_users],
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    })

@bp.route('/users/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    session_user_id = int(session['user_id']) if isinstance(session['user_id'], str) else session['user_id']
    if user_id != session_user_id and not session.get('is_admin'):
        return jsonify({'error': '没有权限'}), 403
    
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    return jsonify(serialize_user(user))

@bp.route('/users', methods=['POST'])
def create_user_api():
    data = request.get_json()
    if not data:
        return jsonify({'error': '请求数据不能为空'}), 400
    
    username = data.get('username', '')
    email = data.get('email', '')
    password = data.get('password', '')
    
    is_valid, error_msg = validate_username(username)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    is_valid, error_msg = validate_email(email)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    is_valid, error_msg = validate_password(password)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    if get_user_by_username(username):
        return jsonify({'error': '用户名已存在'}), 409
    
    if get_user_by_email(email):
        return jsonify({'error': '邮箱已被注册'}), 409
    
    password_hash = generate_password_hash(password)
    user_id = create_user(username, email, password_hash)
    
    user = get_user_by_id(user_id)
    return jsonify(serialize_user(user)), 201

@bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user_api(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': '请求数据不能为空'}), 400
    
    username = data.get('username')
    email = data.get('email')
    is_admin = data.get('is_admin')
    is_active = data.get('is_active')
    
    if username:
        is_valid, error_msg = validate_username(username)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        existing = get_user_by_username(username)
        if existing and existing['id'] != user_id:
            return jsonify({'error': '用户名已存在'}), 409
    
    if email:
        is_valid, error_msg = validate_email(email)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        existing = get_user_by_email(email)
        if existing and existing['id'] != user_id:
            return jsonify({'error': '邮箱已被注册'}), 409
    
    update_user(user_id, username=username, email=email, is_admin=is_admin, is_active=is_active)
    
    user = get_user_by_id(user_id)
    return jsonify(serialize_user(user))

@bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user_api(user_id):
    if user_id == session['user_id']:
        return jsonify({'error': '不能删除自己'}), 400
    
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    delete_user(user_id)
    return jsonify({'message': '用户已删除'})

@bp.route('/auth/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if not data:
        return jsonify({'error': '请求数据不能为空'}), 400
    
    username = data.get('username', '')
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    user = get_user_by_username(username)
    if not user:
        user = get_user_by_email(username)
    
    if user and check_password_hash(user['password_hash'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['is_admin'] = user['is_admin']
        
        return jsonify({
            'message': '登录成功',
            'user': serialize_user(user)
        })
    
    return jsonify({'error': '用户名或密码错误'}), 401

@bp.route('/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'message': '已退出登录'})

@bp.route('/auth/register', methods=['POST'])
def api_register():
    data = request.get_json()
    if not data:
        return jsonify({'error': '请求数据不能为空'}), 400
    
    username = data.get('username', '')
    email = data.get('email', '')
    password = data.get('password', '')
    
    is_valid, error_msg = validate_username(username)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    is_valid, error_msg = validate_email(email)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    is_valid, error_msg = validate_password(password)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    if get_user_by_username(username):
        return jsonify({'error': '用户名已存在'}), 409
    
    if get_user_by_email(email):
        return jsonify({'error': '邮箱已被注册'}), 409
    
    password_hash = generate_password_hash(password)
    user_id = create_user(username, email, password_hash)
    
    user = get_user_by_id(user_id)
    session['user_id'] = user_id
    session['username'] = username
    
    return jsonify({
        'message': '注册成功',
        'user': serialize_user(user)
    }), 201
