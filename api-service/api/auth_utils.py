"""
API Authentication Utilities
Includes: JWT validation, permission checks, and error handling.
"""

from functools import wraps
from flask import request, jsonify, current_app
import jwt
from datetime import datetime, timedelta

# ==========================================
# JWT Validation
# ==========================================
def require_auth(f):
    """
    JWT validation decorator
    Validates the JWT token from Authorization header
    Adds user_id to kwargs if valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            # Log for debugging
            import sys
            print(f"[AUTH DEBUG] No Authorization header in request to {request.path}", file=sys.stderr, flush=True)
            print(f"[AUTH DEBUG] Available headers: {dict(request.headers)}", file=sys.stderr, flush=True)
            return jsonify({
                'success': False,
                'error': 'Authorization header is missing'
            }), 401
        
        # Check if Bearer token format
        try:
            token_type, token = auth_header.split(' ')
            if token_type.lower() != 'bearer':
                print(f"[AUTH DEBUG] Invalid token type: {token_type}")
                return jsonify({
                    'success': False,
                    'error': 'Invalid token type. Use Bearer token'
                }), 401
        except ValueError:
            print(f"[AUTH DEBUG] Invalid Authorization header format: {auth_header}")
            return jsonify({
                'success': False,
                'error': 'Invalid Authorization header format. Use: Bearer <token>'
            }), 401
        
        # Verify JWT token
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            
            # Add user_id to kwargs for the route function
            kwargs['auth_user_id'] = payload['user_id']
            print(f"[AUTH DEBUG] Token validated successfully for user_id: {payload['user_id']}")
            
        except jwt.ExpiredSignatureError:
            print(f"[AUTH DEBUG] Token expired")
            return jsonify({
                'success': False,
                'error': 'Token has expired'
            }), 401
        except jwt.InvalidTokenError as e:
            print(f"[AUTH DEBUG] Invalid token: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Invalid token'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated


def require_owner(resource_type='user'):
    """
    Check resource ownership decorator
    Validates that the authenticated user owns the resource
    
    Args:
        resource_type: Type of resource to check ('user', 'resume', 'cover_letter', 'job')
    
    Usage:
        @require_owner('resume')
        def update_resume(user_id, resume_id):
            # user_id from JWT, resume_id from URL
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # user_id should be added by @require_auth
            authenticated_user_id = kwargs.get('user_id')
            
            if not authenticated_user_id:
                return jsonify({
                    'success': False,
                    'error': 'Authentication required. Use @require_auth before @require_owner'
                }), 401
            
            # Check ownership based on resource type
            if resource_type == 'user':
                # For user resources, check if accessing own profile
                target_user_id = kwargs.get('user_id') or request.view_args.get('user_id')
                if authenticated_user_id != target_user_id:
                    return jsonify({
                        'success': False,
                        'error': 'Access denied. You can only access your own resources'
                    }), 403
            
            elif resource_type in ['resume', 'cover_letter', 'job']:
                # For other resources, verify ownership from database
                resource_id = request.view_args.get(f'{resource_type}_id')
                
                if not resource_id:
                    return jsonify({
                        'success': False,
                        'error': f'{resource_type}_id not found in URL'
                    }), 400
                
                # Check ownership in database
                if not check_resource_ownership(authenticated_user_id, resource_type, resource_id):
                    return jsonify({
                        'success': False,
                        'error': f'Access denied. You do not own this {resource_type}'
                    }), 403
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator


def check_resource_ownership(user_id, resource_type, resource_id):
    """
    Check if user owns the specified resource
    
    Args:
        user_id: ID of the authenticated user
        resource_type: Type of resource ('resume', 'cover_letter', 'job')
        resource_id: ID of the resource to check
    
    Returns:
        bool: True if user owns the resource, False otherwise
    """
    from .utils import get_db
    
    # Map resource types to table names
    table_map = {
        'resume': 'resumes',
        'cover_letter': 'cover_letters',
        'job': 'job_postings'
    }
    
    table_name = table_map.get(resource_type)
    if not table_name:
        return False
    
    try:
        mysql = get_db()
        cursor = mysql.connection.cursor()
        
        query = f"SELECT user_id FROM {table_name} WHERE id = %s"
        cursor.execute(query, (resource_id,))
        result = cursor.fetchone()
        cursor.close()
        
        if result and result.get('user_id') == user_id:
            return True
        
        return False
        
    except Exception as e:
        current_app.logger.error(f'Error checking resource ownership: {str(e)}')
        return False


# ==========================================
# Error Handling
# ==========================================
def handle_errors(f):
    """
    Unified error handling decorator
    Catches all exceptions and returns consistent error response
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            # Validation errors
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
        except PermissionError as e:
            # Permission errors
            return jsonify({
                'success': False,
                'error': str(e)
            }), 403
        except Exception as e:
            # Log the error
            current_app.logger.error(f'Unhandled error in {f.__name__}: {str(e)}')
            
            # Return generic error in production, detailed in development
            if current_app.config['DEBUG']:
                error_message = str(e)
            else:
                error_message = 'An internal error occurred'
            
            return jsonify({
                'success': False,
                'error': error_message
            }), 500
    
    return decorated


def validate_json(f):
    """
    Validate that request contains JSON data
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        if data is None:
            return jsonify({
                'success': False,
                'error': 'Request body must contain valid JSON'
            }), 400
        
        return f(*args, **kwargs)
    
    return decorated


# ==========================================
# JWT Token Generation
# ==========================================
def generate_token(user_id, expires_in_hours=24):
    """
    Generate JWT token for user
    
    Args:
        user_id: ID of the user
        expires_in_hours: Token expiration time in hours (default: 24)
    
    Returns:
        str: JWT token
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )
    
    return token


def generate_refresh_token(user_id, expires_in_days=30):
    """
    Generate refresh token for user
    
    Args:
        user_id: ID of the user
        expires_in_days: Token expiration time in days (default: 30)
    
    Returns:
        str: Refresh token
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=expires_in_days),
        'iat': datetime.utcnow(),
        'type': 'refresh'
    }
    
    token = jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )
    
    return token
