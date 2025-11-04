# api/endpoints/auth.py
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
from ..utils import get_db, success_response, error_response
import jwt

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# -----------------------------
# Sign Up
# -----------------------------
@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    Create a new user account
    POST /api/v1/auth/signup
    Request JSON:
    {
        "first_name": "Yi-Kai",
        "last_name": "Chen",
        "email": "yikai.chen@example.com",
        "password": "123456",
        "phone": "587-123-4567",
        "location": "Calgary",
        "linkedin_profile_url": "https://linkedin.com/in/yikai",
        "github_profile_url": "https://github.com/yikai"
    }
    """
    data = request.get_json()
    required_fields = ['first_name', 'last_name', 'email', 'password', 'phone']

    for field in required_fields:
        if field not in data:
            return error_response(f'{field} is required', 400)
    
    # hash the password
    password_hash = generate_password_hash(data['password'])
    
    mysql = get_db()
    cursor = mysql.connection.cursor()
    
    # Check if email already exists
    cursor.execute("SELECT id FROM users WHERE email = %s", (data['email'],))
    if cursor.fetchone():
        cursor.close()
        return error_response('Email already registered', 400)
    
    # Insert user into DB
    cursor.execute("""
    INSERT INTO users (
        first_name, last_name, email, password, phone, location, linkedin_profile_url, github_profile_url
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
    (
        data['first_name'],
        data['last_name'],
        data['email'],
        password_hash,
        data['phone'],
        data.get('location'),
        data.get('linkedin_profile_url'),
        data.get('github_profile_url')
    ))
    
    mysql.connection.commit()
    user_id = cursor.lastrowid
    cursor.close()
    
    return success_response({'user_id': user_id}, 201)

# -----------------------------
# Login
# -----------------------------
@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return JWT
    POST /api/v1/auth/login
    Request JSON:
    {
        "email": "user@example.com",
        "password": "123456"
    }
    Response JSON:
    {
        "success": true,
        "token": "<JWT_TOKEN>"
    }
    """
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return error_response('Email and password are required', 400)
    
    email = data['email']
    password = data['password']
    
    mysql = get_db()
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, password FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    
    if not user:
        return error_response('Invalid credentials', 401)

    user_id = user['id']
    password_hash = user['password']

    if not check_password_hash(password_hash, password):
        return error_response('Invalid credentials', 401)
    
    # Create JWT token
    secret_key = current_app.config.get('SECRET_KEY', 'mysecret')
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(hours=1)
    }
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    
    return success_response({'token': token})
