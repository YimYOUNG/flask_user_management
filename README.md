# Flask User Management System

**Tech Stack:** Python / Flask / SQLite3 / WTForms / pytest / GitHub Actions / Alibaba Cloud

## Quick Start

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
source venv/bin/activate      # Linux/Mac
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Application
```bash
python run.py
```

Visit http://localhost:5000

## Project Structure
```
flask-user-system/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration
│   ├── routes/              # Routes (auth, user, api)
│   ├── templates/           # HTML templates
│   ├── static/              # CSS/JS
│   └── utils/               # DB, forms, validators
├── tests/                   # pytest tests
├── .github/workflows/       # GitHub Actions
├── users.db                 # SQLite database (auto-generated)
├── requirements.txt
└── run.py
```

## Features
- User registration with validation
- User login/logout
- User management (admin)
- RESTful API for mobile apps
- CSRF protection
- Password hashing (scrypt)
- SQLite3 database with raw SQL
- Database initialization and migration support
- 100% test coverage (488 statements)

## Testing
```bash
pytest tests/ -v
pytest tests/ --cov=app --cov-report=html
```

## Deployment to Alibaba Cloud VPS

### Required Secrets in GitHub
Add these in GitHub repo Settings > Secrets:
- `SERVER_IP`: 8.136.60.141
- `SSH_USER`: root
- `SSH_PASSWORD`: your-password

### Deployment Steps
1. Push code to `main` branch
2. GitHub Actions runs tests
3. If tests pass, deploys to VPS

## API Endpoints
- `POST /api/auth/register` - Register
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/users` - List users (admin)
- `GET/PUT/DELETE /api/users/<id>` - User operations

## First Admin User
Create admin user directly in database or register first user as admin in code.
