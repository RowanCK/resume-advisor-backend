"""
User Endpoints
Handles user profile and related resources
"""

from flask import Blueprint, request, jsonify
from ..auth_utils import require_auth, require_owner, handle_errors
from ..utils import get_db, success_response, error_response, validate_required_fields

user_bp = Blueprint('user', __name__, url_prefix='/user')

# ==========================================
# Get User Profile
# ==========================================
@user_bp.route('/<int:user_id>', methods=['GET'])
@handle_errors
@require_auth
def get_user_profile(auth_user_id, user_id):
    """
    Get user profile by ID
    
    GET /api/v1/user/{user_id}
    
    Response:
    {
        "success": true,
        "data": {
            "id": 101,
            "first_name": "Yi-Kai",
            "last_name": "Chen",
            "email": "user@example.com",
            "phone": "403-xxx-xxxx",
            "location": "Calgary",
            "linkedin_profile_url": "",
            "github_profile_url": ""
        }
    }
    """
    # Check if user is accessing their own profile
    if auth_user_id != user_id:
        return error_response('Access denied. You can only view your own profile', 403)
    
    mysql = get_db()
    cursor = mysql.connection.cursor()
    
    cursor.execute("""
        SELECT id, first_name, last_name, email, phone, location,
               linkedin_profile_url, github_profile_url, created_at
        FROM users
        WHERE id = %s
    """, (user_id,))
    
    user = cursor.fetchone()
    cursor.close()
    
    if not user:
        return error_response('User not found', 404)
    
    return success_response({'data': user})


# ==========================================
# Update User Profile
# ==========================================
@user_bp.route('/<int:user_id>', methods=['PUT'])
@handle_errors
@require_auth
def update_user_profile(auth_user_id, user_id):
    """
    Update user profile
    
    PUT /api/v1/user/{user_id}
    
    Request Body:
    {
        "first_name": "Yi-Kai",
        "last_name": "Chen",
        "phone": "403-xxx-xxxx",
        "location": "Calgary",
        "linkedin_profile_url": "",
        "github_profile_url": ""
    }
    
    Response:
    {
        "success": true,
        "message": "Profile updated successfully"
    }
    """
    # Check if user is updating their own profile
    if auth_user_id != user_id:
        return error_response('Access denied. You can only update your own profile', 403)
    
    data = request.get_json()
    
    if not data:
        return error_response('Request body is required', 400)
    
    # Build dynamic UPDATE query
    allowed_fields = [
        'first_name', 'last_name', 'phone', 'location',
        'linkedin_profile_url', 'github_profile_url'
    ]
    
    update_fields = []
    update_values = []
    
    for field in allowed_fields:
        if field in data:
            update_fields.append(f"{field} = %s")
            update_values.append(data[field])
    
    if not update_fields:
        return error_response('No valid fields to update', 400)
    
    # Add user_id to values
    update_values.append(user_id)
    
    mysql = get_db()
    cursor = mysql.connection.cursor()
    
    query = f"""
        UPDATE users
        SET {', '.join(update_fields)}
        WHERE id = %s
    """
    
    cursor.execute(query, tuple(update_values))
    mysql.connection.commit()
    affected_rows = cursor.rowcount
    cursor.close()
    
    if affected_rows == 0:
        return error_response('User not found', 404)
    
    return success_response({
        'message': 'Profile updated successfully'
    })


# ==========================================
# Get User's Resumes
# ==========================================
@user_bp.route('/<int:user_id>/resumes', methods=['GET'])
@handle_errors
@require_auth
def get_user_resumes(auth_user_id, user_id):
    """
    Get all resumes for a user

    GET /api/v1/user/{user_id}/resumes

    Response:
    {
        "success": true,
        "data": [
            {
                "id": 501,
                "title": "Software Engineer Resume",
                "job_id": 501,
                "last_update": "2025-10-26"
            },
            {
                "id": 502,
                "title": "Data Engineer Resume",
                "job_id": 502,
                "last_update": "2025-09-30"
            }
        ],
        "count": 2
    }
    """
    # Check if user is accessing their own resumes
    if auth_user_id != user_id:
        return error_response('Access denied. You can only view your own resumes', 403)
    
    mysql = get_db()
    cursor = mysql.connection.cursor()
    
    cursor.execute("""
        SELECT id, title, job_id, last_update
        FROM resumes
        WHERE user_id = %s
        ORDER BY last_update DESC
    """, (user_id,))
    
    resumes = cursor.fetchall()
    cursor.close()
    
    return success_response({
        'data': resumes,
        'count': len(resumes)
    })


# ==========================================
# Get User's Cover Letters
# ==========================================
@user_bp.route('/<int:user_id>/coverletters', methods=['GET'])
@handle_errors
@require_auth
def get_user_cover_letters(auth_user_id, user_id):
    """
    Get all cover letters for a user

    GET /api/v1/user/{user_id}/coverletters

    Response:
    {
        "success": true,
        "data": [
            {
                "id": 301,
                "title": "Amazon Cover Letter",
                "last_update": "2025-10-26"
            },
            {
                "id": 302,
                "title": "Google Cover Letter",
                "last_update": "2025-09-20"
            }
        ],
        "count": 2
    }
    """
    # Check if user is accessing their own cover letters
    if auth_user_id != user_id:
        return error_response('Access denied. You can only view your own cover letters', 403)
    
    mysql = get_db()
    cursor = mysql.connection.cursor()
    
    cursor.execute("""
        SELECT id, title, last_update
        FROM cover_letters
        WHERE user_id = %s
        ORDER BY last_update DESC
    """, (user_id,))
    
    cover_letters = cursor.fetchall()
    cursor.close()
    
    return success_response({
        'data': cover_letters,
        'count': len(cover_letters)
    })


# ==========================================
# Get User's Job Postings
# ==========================================
@user_bp.route('/<int:user_id>/jobs', methods=['GET'])
@handle_errors
@require_auth
def get_user_jobs(auth_user_id, user_id):
    """
    Get all saved job postings for a user

    GET /api/v1/user/{user_id}/jobs

    Response:
    {
        "success": true,
        "data": [
            {
                "id": 201,
                "title": "Backend Developer",
                "company": "Google",
                "location": "Toronto",
                "posted_date": "2025-10-15",
                "close_date": "2025-11-15"
            }
        ],
        "count": 1
    }
    """
    # Check if user is accessing their own jobs
    if auth_user_id != user_id:
        return error_response('Access denied. You can only view your own job postings', 403)
    
    mysql = get_db()
    cursor = mysql.connection.cursor()
    
    cursor.execute("""
        SELECT id, title, company, location, posted_date, close_date, created_at
        FROM job_postings
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user_id,))
    
    jobs = cursor.fetchall()
    cursor.close()
    
    return success_response({
        'data': jobs,
        'count': len(jobs)
    })


# ==========================================
# Delete User Account
# ==========================================
@user_bp.route('/<int:user_id>', methods=['DELETE'])
@handle_errors
@require_auth
def delete_user(auth_user_id, user_id):
    """
    Delete user account and all related data

    DELETE /api/v1/user/{user_id}

    Response:
    {
        "success": true,
        "message": "Account deleted successfully"
    }
    
    Note: This will cascade delete all user's resumes, cover letters, and job postings
    """
    # Check if user is deleting their own account
    if auth_user_id != user_id:
        return error_response('Access denied. You can only delete your own account', 403)
    
    mysql = get_db()
    cursor = mysql.connection.cursor()
    
    # Delete user (cascade will handle related records)
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    mysql.connection.commit()
    affected_rows = cursor.rowcount
    cursor.close()
    
    if affected_rows == 0:
        return error_response('User not found', 404)
    
    return success_response({
        'message': 'Account deleted successfully'
    })