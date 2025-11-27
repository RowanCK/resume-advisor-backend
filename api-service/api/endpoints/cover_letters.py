"""
Cover Letter Endpoints
Handles cover letter creation, retrieval, update, and deletion
"""

from flask import Blueprint, request
from datetime import datetime
import json
from ..auth_utils import require_auth, handle_errors
from ..utils import get_db, success_response, error_response, validate_required_fields

cover_letters_bp = Blueprint('cover_letters', __name__, url_prefix='/cover-letters')

# ==========================================
# Get Cover Letter by ID
# ==========================================
@cover_letters_bp.route('/<int:cl_id>', methods=['GET'])
@handle_errors
@require_auth
def get_cover_letter(auth_user_id, cl_id):
    """
    Get cover letter by ID
    ---
    tags:
      - Cover Letters
    summary: Retrieve a specific cover letter by its ID
    security:
      - Bearer: []
    parameters:
      - name: cl_id
        in: path
        type: integer
        required: true
        description: The ID of the cover letter to retrieve
        example: 301
    responses:
      200:
        description: Cover letter retrieved successfully
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
                  example: 301
                title:
                  type: string
                  example: Software Engineer Cover Letter
                job_id:
                  type: integer
                  example: 201
                creation_date:
                  type: string
                  format: date-time
                  example: "2025-10-25 14:30"
                last_updated:
                  type: string
                  format: date-time
                  example: "2025-10-26 16:45"
                content:
                  type: object
                  properties:
                    paragraphs:
                      type: array
                      items:
                        type: string
                      example: ["Dear Hiring Manager,", "I am writing to express my interest..."]
      404:
        description: Cover letter not found
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: Cover letter not found
      403:
        description: Forbidden - Cover letter does not belong to user
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: Forbidden - You do not have access to this cover letter
    """
    mysql = get_db()
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT id, user_id, job_id, title, content,
               DATE_FORMAT(creation_date, '%%Y-%%m-%%d %%H:%%i') as creation_date,
               DATE_FORMAT(last_updated, '%%Y-%%m-%%d %%H:%%i') as last_updated
        FROM cover_letters
        WHERE id = %s
    """, (cl_id,))

    cl = cursor.fetchone()
    cursor.close()

    if not cl:
        return error_response("Cover letter not found", 404)

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
# Save Cover Letter (Create/Update)
# ==========================================
@cover_letters_bp.route('', methods=['POST'])
@handle_errors
@require_auth
def save_cover_letter(auth_user_id):
    """
    Save cover letter content (create new or update existing)
    ---
    tags:
      - Cover Letters
    summary: Create a new cover letter or update an existing one
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        description: Cover letter data to save
        schema:
          type: object
          required:
            - title
            - job_id
            - content
          properties:
            id:
              type: integer
              description: Cover letter ID (optional, for updates)
              example: 301
            title:
              type: string
              example: Software Engineer Cover Letter
            job_id:
              type: integer
              example: 201
            content:
              type: object
              properties:
                paragraphs:
                  type: array
                  items:
                    type: string
                  example: [
                    "Dear Hiring Manager,",
                    "I am writing to express my strong interest in the Software Engineer position at Google. With over 5 years of experience in full-stack development and a proven track record of delivering scalable solutions, I am excited about the opportunity to contribute to your team.",
                    "Thank you for considering my application. I look forward to discussing how my skills and experience align with your needs.",
                    "Sincerely,",
                    "Yi-Kai Chen"
                  ]
    responses:
      201:
        description: Cover letter created successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            cover_letter_id:
              type: integer
              example: 301
            message:
              type: string
              example: Cover letter saved successfully
      200:
        description: Cover letter updated successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            cover_letter_id:
              type: integer
              example: 301
            message:
              type: string
              example: Cover letter updated successfully
      400:
        description: Bad request - missing required fields
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: Missing required field - title
      403:
        description: Forbidden - Cover letter does not belong to user
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: Forbidden - You do not have access to this cover letter
      404:
        description: Cover letter not found (when updating)
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: Cover letter not found
    """
    data = request.get_json()
    
    # Validate required fields
    try:
        validate_required_fields(data, ['title', 'job_id', 'content'])
    except ValueError as e:
        return error_response(str(e), 400)
    
    title = data['title']
    job_id = data['job_id']
    content = data['content']
    cl_id = data.get('id')  # Optional for updates

    mysql = get_db()
    cursor = mysql.connection.cursor()

    # Verify job_id exists
    cursor.execute("SELECT id FROM job_postings WHERE id = %s", (job_id,))
    job = cursor.fetchone()
    if not job:
        cursor.close()
        return error_response(f'Invalid job_id: {job_id} does not exist', 400)
    
    # Convert content to JSON string
    try:
        content_json = json.dumps(content)
    except (TypeError, ValueError) as e:
        cursor.close()
        return error_response(f'Invalid content format: {str(e)}', 400)
    
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # Update existing cover letter
    if cl_id:
        # Verify ownership
        cursor.execute("SELECT user_id FROM cover_letters WHERE id = %s", (cl_id,))
        existing_cl = cursor.fetchone()
        
        if not existing_cl:
            cursor.close()
            return error_response('Cover letter not found', 404)
        
        if existing_cl['user_id'] != auth_user_id:
            cursor.close()
            return error_response('Forbidden - You do not have access to this cover letter', 403)
        
        # Update cover letter
        cursor.execute("""
            UPDATE cover_letters
            SET title = %s, job_id = %s, content = %s, last_updated = %s
            WHERE id = %s
        """, (title, job_id, content_json, current_date, cl_id))
        
        mysql.connection.commit()
        cursor.close()
        
        return success_response({
            'cover_letter_id': cl_id,
            'message': 'Cover letter updated successfully'
        }, 200)
    
    # Create new cover letter
    else:
        cursor.execute("""
            INSERT INTO cover_letters (user_id, job_id, title, content, creation_date, last_updated)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (auth_user_id, job_id, title, content_json, current_date, current_date))
        
        mysql.connection.commit()
        new_cl_id = cursor.lastrowid
        cursor.close()
        
        return success_response({
            'cover_letter_id': new_cl_id,
            'message': 'Cover letter saved successfully'
        }, 201)


# ==========================================
# Delete Cover Letter
# ==========================================
@cover_letters_bp.route('/<int:cl_id>', methods=['DELETE'])
@handle_errors
@require_auth
def delete_cover_letter(auth_user_id, cl_id):
    """
    Delete a cover letter by ID
    ---
    tags:
      - Cover Letters
    summary: Delete a specific cover letter
    security:
      - Bearer: []
    parameters:
      - name: cl_id
        in: path
        type: integer
        required: true
        description: The ID of the cover letter to delete
        example: 301
    responses:
      200:
        description: Cover letter deleted successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: Cover letter deleted successfully
      404:
        description: Cover letter not found
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: Cover letter not found
      403:
        description: Forbidden
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: Forbidden - You do not have access to this cover letter
    """
    mysql = get_db()
    cursor = mysql.connection.cursor()
    
    # Verify ownership
    cursor.execute("SELECT user_id FROM cover_letters WHERE id = %s", (cl_id,))
    cl = cursor.fetchone()
    
    if not cl:
        cursor.close()
        return error_response('Cover letter not found', 404)
    
    if cl['user_id'] != auth_user_id:
        cursor.close()
        return error_response('Forbidden - You do not have access to this cover letter', 403)
    
    # Delete cover letter
    cursor.execute("DELETE FROM cover_letters WHERE id = %s", (cl_id,))
    mysql.connection.commit()
    cursor.close()
    
    return success_response({'message': 'Cover letter deleted successfully'})
