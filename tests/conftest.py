import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), 'test_users.db')

@pytest.fixture(scope='function')
def app():
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['FLASK_DB_PATH'] = TEST_DB_PATH
    
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    app = create_app('testing')
    
    with app.app_context():
        from app.utils.db import init_db
        init_db()
        yield app
        
        with app.app_context():
            from app.utils.db import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users')
            conn.commit()
            conn.close()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
