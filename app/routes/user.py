from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from functools import wraps
from app.utils.forms import UserEditForm
from app.utils.db import get_all_users, get_user_by_id, update_user, delete_user, search_users
from app.utils.validators import validate_username, validate_email

bp = Blueprint('user', __name__, url_prefix='/user')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录', 'error')
            return redirect(url_for('auth.login'))
        if not session.get('is_admin'):
            flash('您没有权限访问此页面', 'error')
            return redirect(url_for('user.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
def dashboard():
    user = get_user_by_id(session['user_id'])
    return render_template('dashboard.html', user=user)

@bp.route('/users')
@admin_required
def users():
    search_query = request.args.get('q', '')
    if search_query:
        users_list = search_users(search_query)
    else:
        users_list = get_all_users()
    return render_template('users.html', users=users_list, search_query=search_query)

@bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        flash('用户不存在', 'error')
        return redirect(url_for('user.users'))
    
    form = UserEditForm(obj=user)
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        
        is_valid, error_msg = validate_username(username)
        if not is_valid:
            flash(error_msg, 'error')
            return render_template('edit_user.html', form=form, user=user)
        
        is_valid, error_msg = validate_email(email)
        if not is_valid:
            flash(error_msg, 'error')
            return render_template('edit_user.html', form=form, user=user)
        
        update_user(
            user_id,
            username=username,
            email=email,
            is_admin=form.is_admin.data,
            is_active=form.is_active.data
        )
        
        flash('用户信息已更新', 'success')
        return redirect(url_for('user.users'))
    
    return render_template('edit_user.html', form=form, user=user)

@bp.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user_route(user_id):
    if user_id == session['user_id']:
        flash('不能删除自己', 'error')
        return redirect(url_for('user.users'))
    
    user = get_user_by_id(user_id)
    if not user:
        flash('用户不存在', 'error')
        return redirect(url_for('user.users'))
    
    delete_user(user_id)
    flash('用户已删除', 'success')
    return redirect(url_for('user.users'))
