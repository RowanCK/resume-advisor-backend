"""
User Endpoints
Handles user profile and related resources
"""

from flask import Blueprint, request
from MySQLdb.cursors import DictCursor
from ..auth_utils import require_auth, handle_errors
from ..utils import get_db, success_response, error_response, validate_required_fields

user_bp = Blueprint('user', __name__, url_prefix='/user')

# ==========================================
# Get User Profile
# ==========================================
@user_bp.route('', methods=['GET'])
@handle_errors
@require_auth
def get_user_profile(auth_user_id):
    """
    Get user profile by ID
    ---
    tags:
      - User
    summary: Retrieve the authenticated user's profile
    security:
      - Bearer: []
    responses:
      200:
        description: User profile retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                id:
                  type: integer
                  example: 101
                first_name:
                  type: string
                  example: Yi-Kai
                last_name:
                  type: string
                  example: Chen
                email:
                  type: string
                  example: user@example.com
                phone:
                  type: string
                  example: 403-xxx-xxxx
                location:
                  type: string
                  example: Calgary
                linkedin_profile_url:
                  type: string
                  example: ""
                github_profile_url:
                  type: string
                  example: ""
      404:
        description: User not found
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: User not found
    """
    
    mysql = get_db()
    cursor = mysql.connection.cursor()
    
    cursor.execute("""
        SELECT id, first_name, last_name, email, phone, location,
               linkedin, github
        FROM users
        WHERE id = %s
    """, (auth_user_id,))
    
    user = cursor.fetchone()
    cursor.close()
    
    if not user:
        return error_response('User not found', 404)
    
    return success_response({'data': user})


# ==========================================
# Update User Profile
# ==========================================
@user_bp.route('', methods=['PUT'])
@handle_errors
@require_auth
def update_user_profile(auth_user_id):
    """
    Update user profile
    ---
    tags:
      - User
    summary: Update the authenticated user's profile
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            first_name:
              type: string
              example: Yi-Kai
            last_name:
              type: string
              example: Chen
            phone:
              type: string
              example: 403-xxx-xxxx
            location:
              type: string
              example: Calgary
            linkedin:
              type: string
              example: ""
            github:
              type: string
              example: ""
    responses:
      200:
        description: Profile updated successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: Profile updated successfully
      400:
        description: Invalid request or no fields to update
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: No valid fields to update
      404:
        description: User not found
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: User not found
    """

    data = request.get_json()
    
    if not data:
        return error_response('Request body is required', 400)
    
    # Build dynamic UPDATE query
    allowed_fields = [
        'first_name', 'last_name', 'phone', 'location',
        'linkedin', 'github'
    ]
    
    update_fields = []
    update_values = []
    
    for field in allowed_fields:
        if field in data:
            update_fields.append(f"{field} = %s")
            update_values.append(data[field])
    
    if not update_fields:
        return error_response('No valid fields to update', 400)
    
    mysql = get_db()
    cursor = mysql.connection.cursor()
    
    # First, check if user exists
    cursor.execute("SELECT id FROM users WHERE id = %s", (auth_user_id,))
    user = cursor.fetchone()
    
    if not user:
        cursor.close()
        return error_response('User not found', 404)
    
    # Add user_id to values
    update_values.append(auth_user_id)
    
    query = f"""
        UPDATE users
        SET {', '.join(update_fields)}
        WHERE id = %s
    """
    
    cursor.execute(query, tuple(update_values))
    mysql.connection.commit()
    cursor.close()
    
    return success_response({
        'message': 'Profile updated successfully'
    })


# ==========================================
# Get User's Resumes
# ==========================================
@user_bp.route('/resumes', methods=['GET'])
@handle_errors
@require_auth
def get_user_resumes(auth_user_id):
    """
    Get all resumes for a user
    ---
    tags:
      - User
    summary: Retrieve all resumes for the authenticated user
    security:
      - Bearer: []
    responses:
      200:
        description: User resumes retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 501
                  title:
                    type: string
                    example: Software Engineer Resume
                  job_id:
                    type: integer
                    example: 501
                  last_updated:
                    type: string
                    format: date
                    example: 2025-10-26
            count:
              type: integer
              example: 2
    """

    mysql = get_db()
    cursor = mysql.connection.cursor()
    
    cursor.execute("""
        SELECT id, title, job_id, last_updated
        FROM resumes
        WHERE user_id = %s
        ORDER BY last_updated DESC
    """, (auth_user_id,))
    
    resumes = cursor.fetchall()
    cursor.close()
    
    return success_response({
        'data': resumes,
        'count': len(resumes)
    })


# ==========================================
# Get User's Cover Letters
# ==========================================
@user_bp.route('/coverletters', methods=['GET'])
@handle_errors
@require_auth
def get_user_cover_letters(auth_user_id):
    """
    Get all cover letters for a user
    ---
    tags:
      - User
    summary: Retrieve all cover letters for the authenticated user
    security:
      - Bearer: []
    responses:
      200:
        description: User cover letters retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 301
                  title:
                    type: string
                    example: Amazon Cover Letter
                  last_updated:
                    type: string
                    format: date
                    example: 2025-10-26
            count:
              type: integer
              example: 2
    """

    mysql = get_db()
    cursor = mysql.connection.cursor()
    
    cursor.execute("""
        SELECT id, title, last_updated
        FROM cover_letters
        WHERE user_id = %s
        ORDER BY last_updated DESC
    """, (auth_user_id,))
    
    cover_letters = cursor.fetchall()
    cursor.close()
    
    return success_response({
        'data': cover_letters,
        'count': len(cover_letters)
    })


# ==========================================
# Get User's Job Postings
# ==========================================
@user_bp.route('/jobs', methods=['GET'])
@handle_errors
@require_auth
def get_user_jobs(auth_user_id):
    """
    Get all saved job postings for a user based on resumes
    ---
    tags:
      - User
    summary: Retrieve all job postings saved by the authenticated user
    security:
      - Bearer: []
    responses:
      200:
        description: User job postings retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 201
                  title:
                    type: string
                    example: Backend Developer
                  company:
                    type: string
                    example: Google
                  location:
                    type: string
                    example: Toronto
                  posted_date:
                    type: string
                    format: date
                    example: 2025-10-15
                  close_date:
                    type: string
                    format: date
                    example: 2025-11-15
            count:
              type: integer
              example: 1
    """

    mysql = get_db()
    cursor = mysql.connection.cursor(DictCursor)
    
    cursor.execute("""
        SELECT
            jp.id,
            jp.title,
            c.name AS company,
            jp.job_location AS location,
            jp.posted_date,
            jp.close_date
        FROM resumes r
        JOIN job_postings jp ON r.job_id = jp.id
        JOIN company c ON jp.company_id = c.id
        WHERE r.user_id = %s
        ORDER BY r.last_updated DESC
    """, (auth_user_id,))
    
    jobs = cursor.fetchall()
    cursor.close()
    
    return success_response({
        'data': jobs,
        'count': len(jobs)
    })


# ==========================================
# Delete User Account
# ==========================================
@user_bp.route('', methods=['DELETE'])
@handle_errors
@require_auth
def delete_user(auth_user_id):
    """
    Delete user account and all related data
    ---
    tags:
      - User
    summary: Delete the authenticated user's account along with all resumes, cover letters, and related job postings
    security:
      - Bearer: []
    responses:
      200:
        description: Account deleted successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: Account deleted successfully
      404:
        description: User not found
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: User not found
    """

    mysql = get_db()
    cursor = mysql.connection.cursor()
    
    # Delete user (cascade will handle related records)
    cursor.execute("DELETE FROM users WHERE id = %s", (auth_user_id,))
    mysql.connection.commit()
    affected_rows = cursor.rowcount
    cursor.close()
    
    if affected_rows == 0:
        return error_response('User not found', 404)
    
    return success_response({
        'message': 'Account deleted successfully'
    })