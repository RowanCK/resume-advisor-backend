# api/endpoints/auth.py
from flask import Blueprint, request, current_app
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
    ---
    tags:
      - Authentication
    summary: Create a new user account
    description: Register a new user with profile information.
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - first_name
            - last_name
            - email
            - password
            - phone
          properties:
            first_name:
              type: string
              example: Rowan
            last_name:
              type: string
              example: Chen
            email:
              type: string
              example: user@example.com
            password:
              type: string
              example: "123456"
            phone:
              type: string
              example: 587-123-4567
            location:
              type: string
              example: Calgary
            linkedin_profile_url:
              type: string
              example: https://linkedin.com/in/yikai
            github_profile_url:
              type: string
              example: https://github.com/yikai
    responses:
      201:
        description: User created successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            user_id:
              type: integer
              example: 12
      400:
        description: Missing fields or email already exists
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: Email already registered
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
        first_name, last_name, email, password, phone, location, linkedin, github
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
    Authenticate user and return JWT token
    ---
    tags:
      - Authentication
    summary: User login
    description: Authenticate a user using email and password and return a JWT token.
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: user@example.com
            password:
              type: string
              example: "123456"
    responses:
      200:
        description: Successfully authenticated
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            user_id:
              type: integer
              example: 12
            token:
              type: string
              example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
      400:
        description: Missing email or password
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: Email and password are required
      401:
        description: Invalid credentials
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: Invalid credentials
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
    
    return success_response({'user_id': user_id, 'user_email': email, 'token': token})
