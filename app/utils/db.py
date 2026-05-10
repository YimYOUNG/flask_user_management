import os
import sqlite3
from contextlib import contextmanager
from app.config import Config

DATABASE_PATH = os.environ.get('FLASK_DB_PATH') or Config.SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def get_db():
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(256) NOT NULL,
                is_admin BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        conn.commit()

def get_user_by_id(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        return cursor.fetchone()

def get_user_by_username(username):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        return cursor.fetchone()

def get_user_by_email(email):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        return cursor.fetchone()

def create_user(username, email, password_hash, is_admin=False):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (username, email, password_hash, is_admin) VALUES (?, ?, ?, ?)',
            (username, email, password_hash, is_admin)
        )
        return cursor.lastrowid

def update_user_login(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
            (user_id,)
        )

def get_all_users():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email, is_admin, is_active, created_at, last_login FROM users ORDER BY created_at DESC')
        return cursor.fetchall()

def update_user(user_id, username=None, email=None, is_admin=None, is_active=None):
    updates = []
    params = []
    if username is not None:
        updates.append('username = ?')
        params.append(username)
    if email is not None:
        updates.append('email = ?')
        params.append(email)
    if is_admin is not None:
        updates.append('is_admin = ?')
        params.append(is_admin)
    if is_active is not None:
        updates.append('is_active = ?')
        params.append(is_active)
    
    if updates:
        params.append(user_id)
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", params)

def delete_user(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))

def search_users(query):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, username, email, is_admin, is_active, created_at, last_login FROM users WHERE username LIKE ? OR email LIKE ?',
            (f'%{query}%', f'%{query}%')
        )
        return cursor.fetchall()
