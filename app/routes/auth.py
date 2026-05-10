from flask import Blueprint, render_template, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.forms import RegistrationForm, LoginForm
from app.utils.db import create_user, get_user_by_username, get_user_by_email, update_user_login
from flask import current_app

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('user.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        
        existing_user = get_user_by_username(username)
        if existing_user:
            flash('用户名已存在', 'error')
            return render_template('register.html', form=form)
        
        existing_email = get_user_by_email(email)
        if existing_email:
            flash('邮箱已被注册', 'error')
            return render_template('register.html', form=form)
        
        password_hash = generate_password_hash(password)
        user_id = create_user(username, email, password_hash)
        
        session['user_id'] = user_id
        session['username'] = username
        session.permanent = current_app.config.get('PERMANENT_SESSION_LIFETIME') is not None
        
        flash('注册成功！', 'success')
        return redirect(url_for('user.dashboard'))
    
    return render_template('register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('user.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = get_user_by_username(username)
        if not user:
            user = get_user_by_email(username)
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            session.permanent = form.remember.data
            
            update_user_login(user['id'])
            
            flash('登录成功！', 'success')
            next_page = url_for('user.dashboard')
            return redirect(next_page)
        else:
            flash('用户名或密码错误', 'error')
    
    return render_template('login.html', form=form)

@bp.route('/logout')
def logout():
    session.clear()
    flash('您已成功退出登录', 'success')
    return redirect(url_for('auth.login'))
