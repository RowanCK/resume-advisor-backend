"""
Cover Letter Endpoints
Handles cover letter creation, retrieval, update, and deletion
"""

from flask import Blueprint, request
from datetime import datetime
import json
from ..auth_utils import require_auth, handle_errors
from ..utils import get_db, success_response, error_response, validate_required_fields

cover_letters_bp = Blueprint('cover_letters', __name__, url_prefix='/cover_letters')

# ==========================================
# Create Cover Letter
# ==========================================
@cover_letters_bp.route('', methods=['POST'])
@handle_errors
@require_auth
def create_cover_letter(auth_user_id):
    """
    Create a new cover letter
    """
    required_fields = ['title', 'job_id', 'content']
    data = request.json

    if not validate_required_fields(data, required_fields):
        return error_response("Missing required fields", 400)

    mysql = get_db()
    cursor = mysql.connection.cursor()

    cursor.execute("""
        INSERT INTO cover_letters (user_id, job_id, title, content, creation_date, last_updated)
        VALUES (%s, %s, %s, %s, NOW(), NOW())
    """, (auth_user_id, data['job_id'], data['title'], json.dumps(data['content'])))

    mysql.connection.commit()
    new_id = cursor.lastrowid
    cursor.close()

    return success_response({
        'message': 'Cover letter created successfully',
        'id': new_id
    })


# ==========================================
# Get Cover Letter by ID
# ==========================================
@cover_letters_bp.route('/<int:cl_id>', methods=['GET'])
@handle_errors
@require_auth
def get_cover_letter(auth_user_id, cl_id):
    """
    Retrieve cover letter by ID
    """
    mysql = get_db()
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT id, user_id, job_id, title, content,
               DATE_FORMAT(creation_date, '%%Y-%%m-%%d') as creation_date,
               DATE_FORMAT(last_updated, '%%Y-%%m-%%d') as last_updated
        FROM cover_letters
        WHERE id = %s
    """, (cl_id,))

    cl = cursor.fetchone()
    cursor.close()

    if not cl:
        return error_response("Cover Letter not found", 404)

    if cl['user_id'] != auth_user_id:
        return error_response("Forbidden - You do not have access to this cover letter", 403)

    try:
        content = json.loads(cl['content'])
    except json.JSONDecodeError:
        content = {}

    response_data = {
        'id': cl['id'],
        'title': cl['title'],
        'job_id': cl['job_id'],
        'creation_date': cl['creation_date'],
        'last_updated': cl['last_updated'],
        'content': content
    }

    return success_response({'data': response_data})


# ==========================================
# Update Cover Letter
# ==========================================
@cover_letters_bp.route('/<int:cl_id>', methods=['PUT'])
@handle_errors
@require_auth
def update_cover_letter(auth_user_id, cl_id):
    """
    Update an existing cover letter
    """
    data = request.json

    mysql = get_db()
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT user_id FROM cover_letters WHERE id = %s", (cl_id,))
    cl = cursor.fetchone()

    if not cl:
        cursor.close()
        return error_response("Cover Letter not found", 404)

    if cl['user_id'] != auth_user_id:
        cursor.close()
        return error_response("Forbidden - You do not have access to this cover letter", 403)

    # Build update set
    update_fields = []
    params = []

    if 'title' in data:
        update_fields.append("title = %s")
        params.append(data['title'])

    if 'job_id' in data:
        update_fields.append("job_id = %s")
        params.append(data['job_id'])

    if 'content' in data:
        update_fields.append("content = %s")
        params.append(json.dumps(data['content']))

    if not update_fields:
        cursor.close()
        return error_response("No fields to update", 400)

    update_fields.append("last_updated = NOW()")

    params.append(cl_id)

    cursor.execute(f"""
        UPDATE cover_letters
        SET {', '.join(update_fields)}
        WHERE id = %s
    """, tuple(params))

    mysql.connection.commit()
    cursor.close()

    return success_response({'message': 'Cover letter updated successfully'})


# ==========================================
# Delete Cover Letter
# ==========================================
@cover_letters_bp.route('/<int:cl_id>', methods=['DELETE'])
@handle_errors
@require_auth
def delete_cover_letter(auth_user_id, cl_id):
    """
    Delete a cover letter
    """
    mysql = get_db()
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT user_id FROM cover_letters WHERE id = %s", (cl_id,))
    cl = cursor.fetchone()

    if not cl:
        cursor.close()
        return error_response("Cover Letter not found", 404)

    if cl['user_id'] != auth_user_id:
        cursor.close()
        return error_response("Forbidden - You do not have access to this cover letter", 403)

    cursor.execute("DELETE FROM cover_letters WHERE id = %s", (cl_id,))
    mysql.connection.commit()
    cursor.close()

    return success_response({'message': 'Cover letter deleted successfully'})
