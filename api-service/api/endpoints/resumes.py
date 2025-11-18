"""
Resume Endpoints
Handles resume creation, retrieval, and management
"""

from flask import Blueprint, request
from datetime import datetime
import json
from ..auth_utils import require_auth, handle_errors
from ..utils import get_db, success_response, error_response, validate_required_fields

resumes_bp = Blueprint('resumes', __name__, url_prefix='/resumes')

# ==========================================
# Get Resume by ID
# ==========================================
@resumes_bp.route('/<int:resume_id>', methods=['GET'])
@handle_errors
@require_auth
def get_resume(auth_user_id, resume_id):
    """
    Get resume by ID
    ---
    tags:
      - Resumes
    summary: Retrieve a specific resume by its ID
    security:
      - Bearer: []
    parameters:
      - name: resume_id
        in: path
        type: integer
        required: true
        description: The ID of the resume to retrieve
        example: 501
    security:
      - Bearer: []
    responses:
      200:
        description: Resume retrieved successfully
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
                  example: 501
                title:
                  type: string
                  example: Software Engineer Resume
                job_id:
                  type: integer
                  example: 201
                creation_date:
                  type: string
                  format: date
                  example: "2025-10-25"
                last_updated:
                  type: string
                  format: date
                  example: "2025-10-26"
                sections:
                  type: object
                  properties:
                    order:
                      type: array
                      items:
                        type: string
                      example: ["education", "work_experience", "projects", "skills"]
                    education:
                      type: array
                      items:
                        type: object
                    work_experience:
                      type: array
                      items:
                        type: object
                    projects:
                      type: array
                      items:
                        type: object
                    skills:
                      type: array
                      items:
                        type: object
      404:
        description: Resume not found
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: Resume not found
      403:
        description: Forbidden - Resume does not belong to user
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: Forbidden - You do not have access to this resume
    """
    mysql = get_db()
    cursor = mysql.connection.cursor()
    
    # Fetch resume and verify ownership
    cursor.execute("""
        SELECT id, user_id, job_id, title, content, 
               DATE_FORMAT(creation_date, '%%Y-%%m-%%d') as creation_date,
               DATE_FORMAT(last_updated, '%%Y-%%m-%%d') as last_updated
        FROM resumes
        WHERE id = %s
    """, (resume_id,))
    
    resume = cursor.fetchone()
    cursor.close()
    
    if not resume:
        return error_response('Resume not found', 404)
    
    # Verify user owns this resume
    if resume['user_id'] != auth_user_id:
        return error_response('Forbidden - You do not have access to this resume', 403)
    
    # Parse the content JSON
    try:
        sections = json.loads(resume['content'])
    except json.JSONDecodeError:
        sections = {}
    
    # Build response
    response_data = {
        'id': resume['id'],
        'title': resume['title'],
        'job_id': resume['job_id'],
        'creation_date': resume['creation_date'],
        'last_updated': resume['last_updated'],
        'sections': sections
    }
    
    return success_response({'data': response_data})


# ==========================================
# Save Resume (Create/Update)
# ==========================================
@resumes_bp.route('', methods=['POST'])
@handle_errors
@require_auth
def save_resume(auth_user_id):
    """
    Save resume content (create new or update existing)
    ---
    tags:
      - Resumes
    summary: Create a new resume or update an existing one
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        description: Resume data to save
        schema:
          type: object
          required:
            - title
            - job_id
            - sections
          properties:
            id:
              type: integer
              description: Resume ID (optional, for updates)
              example: 501
            title:
              type: string
              example: Software Engineer Resume
            job_id:
              type: integer
              example: 201
            sections:
              type: object
              properties:
                order:
                  type: array
                  items:
                    type: string
                  example: ["education", "work_experience", "projects", "skills"]
                education:
                  type: array
                  items:
                    type: object
                  example: [
                    {
                      "id": "1",
                      "universityName": "State University",
                      "degree": "Bachelor of Science in Computer Science",
                      "location": "City, State",
                      "datesAttended": "Sep. 2017 – May 2021",
                      "coursework": ["Data Structures", "Software Methodology"],
                      "order": 0
                    }
                  ]
                work_experience:
                  type: array
                  items:
                    type: object
                projects:
                  type: array
                  items:
                    type: object
                skills:
                  type: array
                  items:
                    type: object
    security:
      - Bearer: []
    responses:
      201:
        description: Resume created successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            resume_id:
              type: integer
              example: 501
            message:
              type: string
              example: Resume saved successfully
      200:
        description: Resume updated successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            resume_id:
              type: integer
              example: 501
            message:
              type: string
              example: Resume updated successfully
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
        description: Forbidden - Resume does not belong to user
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: Forbidden - You do not have access to this resume
    """
    data = request.get_json()
    
    # Validate required fields
    try:
        validate_required_fields(data, ['title', 'job_id', 'sections'])
    except ValueError as e:
        return error_response(str(e), 400)
    
    title = data['title']
    job_id = data['job_id']
    sections = data['sections']
    resume_id = data.get('id')  # Optional for updates
    
    # Convert sections to JSON string
    try:
        content_json = json.dumps(sections)
    except (TypeError, ValueError) as e:
        return error_response(f'Invalid sections format: {str(e)}', 400)
    
    mysql = get_db()
    cursor = mysql.connection.cursor()
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # Update existing resume
    if resume_id:
        # Verify ownership
        cursor.execute("SELECT user_id FROM resumes WHERE id = %s", (resume_id,))
        existing_resume = cursor.fetchone()
        
        if not existing_resume:
            cursor.close()
            return error_response('Resume not found', 404)
        
        if existing_resume['user_id'] != auth_user_id:
            cursor.close()
            return error_response('Forbidden - You do not have access to this resume', 403)
        
        # Update resume
        cursor.execute("""
            UPDATE resumes
            SET title = %s, job_id = %s, content = %s, last_updated = %s
            WHERE id = %s
        """, (title, job_id, content_json, current_date, resume_id))
        
        mysql.connection.commit()
        cursor.close()
        
        return success_response({
            'resume_id': resume_id,
            'message': 'Resume updated successfully'
        }, 200)
    
    # Create new resume
    else:
        cursor.execute("""
            INSERT INTO resumes (user_id, job_id, title, content, creation_date, last_updated)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (auth_user_id, job_id, title, content_json, current_date, current_date))
        
        mysql.connection.commit()
        new_resume_id = cursor.lastrowid
        cursor.close()
        
        return success_response({
            'resume_id': new_resume_id,
            'message': 'Resume saved successfully'
        }, 201)


# ==========================================
# Delete Resume
# ==========================================
@resumes_bp.route('/<int:resume_id>', methods=['DELETE'])
@handle_errors
@require_auth
def delete_resume(auth_user_id, resume_id):
    """
    Delete a resume by ID
    ---
    tags:
      - Resumes
    summary: Delete a specific resume
    security:
      - Bearer: []
    parameters:
      - name: resume_id
        in: path
        type: integer
        required: true
        description: The ID of the resume to delete
        example: 501
    security:
      - Bearer: []
    responses:
      200:
        description: Resume deleted successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: Resume deleted successfully
      404:
        description: Resume not found
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: Resume not found
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
              example: Forbidden - You do not have access to this resume
    """
    mysql = get_db()
    cursor = mysql.connection.cursor()
    
    # Verify ownership
    cursor.execute("SELECT user_id FROM resumes WHERE id = %s", (resume_id,))
    resume = cursor.fetchone()
    
    if not resume:
        cursor.close()
        return error_response('Resume not found', 404)
    
    if resume['user_id'] != auth_user_id:
        cursor.close()
        return error_response('Forbidden - You do not have access to this resume', 403)
    
    # Delete resume
    cursor.execute("DELETE FROM resumes WHERE id = %s", (resume_id,))
    mysql.connection.commit()
    cursor.close()
    
    return success_response({'message': 'Resume deleted successfully'})