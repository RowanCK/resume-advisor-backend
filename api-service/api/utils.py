"""
API Utilities
Includes: database operations, validation helpers, response formatting, and encryption utilities.
"""

from flask import current_app, jsonify
import bcrypt
import re

# ==========================================
# Database Utilities
# ==========================================
def get_db():
    """
    Get the current application's MySQL database connection
    
    Returns:
        mysql (Flask-MySQL): MySQL connection instance
    """
    return current_app.mysql


def execute_query(query, params=None, fetchone=False):
    """
    Execute SQL query
    
    Args:
        query (str): SQL query string
        params (tuple): Query parameters (optional)
        fetchone (bool): Whether to fetch a single record
    
    Returns:
        dict | list[dict]: Query result(s)
    """
    mysql = get_db()
    cursor = mysql.connection.cursor()
    
    cursor.execute(query, params or ())
    
    result = cursor.fetchone() if fetchone else cursor.fetchall()
    
    cursor.close()
    return result


# ==========================================
# Validation Utilities
# ==========================================
def validate_email(email):
    """
    Validate email format using regex
    
    Args:
        email (str): Email string to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


def validate_required_fields(data, required_fields):
    """
    Ensure required fields exist and are not empty
    
    Args:
        data (dict): Request JSON data
        required_fields (list[str]): List of required field names
    
    Raises:
        ValueError: If any required field is missing or empty
    """
    for field in required_fields:
        if field not in data or data[field] in (None, '', []):
            raise ValueError(f'Missing required field: {field}')


# ==========================================
# Response Formatting
# ==========================================
def success_response(data=None, status=200):
    """
    Return a standardized success JSON response
    
    Args:
        data (dict): Additional data to include in response
        status (int): HTTP status code
    
    Returns:
        Response: Flask JSON response
    """
    payload = {'success': True}
    if data:
        payload.update(data)
    
    return jsonify(payload), status


def error_response(message, status=400):
    """
    Return a standardized error JSON response
    
    Args:
        message (str): Error message
        status (int): HTTP status code
    
    Returns:
        Response: Flask JSON response
    """
    return jsonify({
        'success': False,
        'error': message
    }), status


# ==========================================
# Encryption Utilities
# ==========================================
def hash_password(password):
    """
    Hash a plaintext password using bcrypt
    
    Args:
        password (str): Plaintext password
    
    Returns:
        bytes: Hashed password
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def verify_password(password, hashed):
    """
    Verify that a plaintext password matches a hashed password
    
    Args:
        password (str): Plaintext password
        hashed (bytes): Hashed password
    
    Returns:
        bool: True if password matches, False otherwise
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed)
