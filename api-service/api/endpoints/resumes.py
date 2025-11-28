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
                  format: date-time
                  example: "2025-10-25 14:30"
                last_updated:
                  type: string
                  format: date-time
                  example: "2025-10-26 16:45"
                sections:
                  type: object
                  properties:
                    order:
                      type: array
                      items:
                        type: string
                      example: ["education", "work_experience", "leadership", "projects", "skills"]
                    education:
                      type: array
                      items:
                        type: object
                    work_experience:
                      type: array
                      items:
                        type: object
                    leadership:
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
               DATE_FORMAT(creation_date, '%%Y-%%m-%%d %%H:%%i') as creation_date,
               DATE_FORMAT(last_updated, '%%Y-%%m-%%d %%H:%%i') as last_updated
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
                  example: ["education", "work_experience", "leadership", "projects", "skills"]
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
                leadership:
                  type: array
                  items:
                    type: object
                  example: [
                    {
                      "id": "1",
                      "position": "President, Computer Science Club",
                      "organization": "State University",
                      "location": "City, State",
                      "dates": "Sep. 2019 – May 2021",
                      "responsibilities": ["Led team of 20 members", "Organized hackathons"],
                      "order": 0
                    }
                  ]
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

    mysql = get_db()
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT id FROM job_postings WHERE id = %s", (job_id,))
    job = cursor.fetchone()
    if not job:
        cursor.close()
        return error_response(f'Invalid job_id: {job_id} does not exist', 400)
    
    # Convert sections to JSON string
    try:
        content_json = json.dumps(sections)
    except (TypeError, ValueError) as e:
        return error_response(f'Invalid sections format: {str(e)}', 400)
    
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M')
    
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

        _sync_resume_data_to_tables(cursor, auth_user_id, sections)
        
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

        _sync_resume_data_to_tables(cursor, auth_user_id, sections)
        
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


# ==========================================
# Helper Function: Sync Resume Data to Tables
# ==========================================
def _sync_resume_data_to_tables(cursor, user_id, sections):
    """
    Sync resume sections data to individual database tables for analysis.
    This maintains the existing content JSON storage while also populating
    normalized tables.
    """
    
    # ==========================================
    # Sync Education
    # ==========================================
    if 'education' in sections and sections['education']:
        for edu in sections['education']:
            school = edu.get('universityName', '')[:50]  # Limit to 50 chars
            degree = edu.get('degree', '')[:50] if edu.get('degree') else None
            
            # Parse dates from "Sep. 2017 – May 2021" format
            dates_str = edu.get('datesAttended', '')
            start_date, end_date = _parse_date_range(dates_str)
            
            if school:  # Only insert if school name exists
                # Check if education already exists
                cursor.execute("""
                    SELECT id FROM education 
                    WHERE user_id = %s AND school = %s AND degree = %s
                """, (user_id, school, degree))
                
                existing = cursor.fetchone()
                
                if not existing:
                    cursor.execute("""
                        INSERT INTO education (user_id, school, degree, start_date, end_date)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (user_id, school, degree, start_date, end_date))
    
    # ==========================================
    # Sync Work Experience
    # ==========================================
    if 'work_experience' in sections and sections['work_experience']:
        for work in sections['work_experience']:
            job_title = work.get('jobTitle', '')[:50]
            
            # Parse dates
            dates_str = work.get('dates', '')
            start_date, end_date = _parse_date_range(dates_str)
            
            if job_title and start_date:  # job_title and start_date are required
                # Check if work experience already exists
                cursor.execute("""
                    SELECT id FROM work_experiences 
                    WHERE user_id = %s AND job_title = %s AND start_date = %s
                """, (user_id, job_title, start_date))
                
                existing = cursor.fetchone()
                
                if not existing:
                    cursor.execute("""
                        INSERT INTO work_experiences (user_id, job_title, start_date, end_date)
                        VALUES (%s, %s, %s, %s)
                    """, (user_id, job_title, start_date, end_date))
    
    # ==========================================
    # Sync Projects
    # ==========================================
    if 'projects' in sections and sections['projects']:
        for project in sections['projects']:
            project_title = project.get('title', '')[:50]
            description = project.get('description', '')[:200] if project.get('description') else None
            
            # Parse dates
            dates_str = project.get('dates', '')
            start_date, end_date = _parse_date_range(dates_str)
            
            if project_title:  # Only insert if title exists
                # Check if project already exists
                cursor.execute("""
                    SELECT id FROM projects 
                    WHERE user_id = %s AND title = %s
                """, (user_id, project_title))
                
                existing = cursor.fetchone()
                
                if not existing:
                    cursor.execute("""
                        INSERT INTO projects (user_id, title, start_date, end_date, description)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (user_id, project_title, start_date, end_date, description))
    

    # ==========================================
    # Sync Skills
    # ==========================================
    if 'skills' in sections and sections['skills']:
        # Clear existing user skills mapping
        cursor.execute("DELETE FROM user_skill_map WHERE user_id = %s", (user_id,))
        
        skills_data = sections['skills']
        
        # Handle both formats:
        # Format 1: {"languages": "Python, Java", "developerTools": "Git"}
        # Format 2: [{"category": "Languages", "items": ["Python", "Java"]}]
        
        if isinstance(skills_data, dict):
            # Format 1: Dictionary with categories as keys
            for category_key, skills_str in skills_data.items():
                if not skills_str:
                    continue
                
                # Convert camelCase to readable format
                category = category_key.replace('_', ' ').title()
                if category_key == 'languages':
                    category = 'Languages'
                elif category_key == 'developerTools':
                    category = 'Developer Tools'
                elif category_key == 'technologiesFrameworks':
                    category = 'Technologies & Frameworks'
                
                # Split comma-separated skills
                if isinstance(skills_str, str):
                    skill_items = [s.strip() for s in skills_str.split(',') if s.strip()]
                else:
                    skill_items = []
                
                # Insert each skill
                for skill_name in skill_items:
                    if skill_name:
                        skill_name = skill_name.strip()[:50]
                        
                        # Check if skill exists
                        cursor.execute("SELECT id FROM skills WHERE name = %s", (skill_name,))
                        skill = cursor.fetchone()
                        
                        if skill:
                            skill_id = skill['id']
                        else:
                            # Create new skill
                            cursor.execute("""
                                INSERT INTO skills (name, category)
                                VALUES (%s, %s)
                            """, (skill_name, category))
                            skill_id = cursor.lastrowid
                        
                        # Map user to skill
                        cursor.execute("""
                            INSERT INTO user_skill_map (user_id, skill_id)
                            VALUES (%s, %s)
                            ON DUPLICATE KEY UPDATE skill_id = skill_id
                        """, (user_id, skill_id))
        
        elif isinstance(skills_data, list):
            # Format 2: Array of skill categories
            for skill_category in skills_data:
                if not isinstance(skill_category, dict):
                    continue
                
                category = skill_category.get('category', 'Other')
                items = skill_category.get('items', [])
                
                for skill_name in items:
                    if skill_name:
                        skill_name = skill_name.strip()[:50]
                        
                        # Check if skill exists
                        cursor.execute("SELECT id FROM skills WHERE name = %s", (skill_name,))
                        skill = cursor.fetchone()
                        
                        if skill:
                            skill_id = skill['id']
                        else:
                            # Create new skill
                            cursor.execute("""
                                INSERT INTO skills (name, category)
                                VALUES (%s, %s)
                            """, (skill_name, category))
                            skill_id = cursor.lastrowid
                        
                        # Map user to skill
                        cursor.execute("""
                            INSERT INTO user_skill_map (user_id, skill_id)
                            VALUES (%s, %s)
                            ON DUPLICATE KEY UPDATE skill_id = skill_id
                        """, (user_id, skill_id))


# ==========================================
# Helper Function: Parse Date Range
# ==========================================
def _parse_date_range(dates_str):
    """
    Parse date range string like "Sep. 2017 – May 2021" or "Jun. 2021 – Present"
    Returns (start_date, end_date) as strings in 'YYYY-MM-DD' format or None
    """
    if not dates_str:
        return None, None
    
    # Split by various dash characters
    dates_str = dates_str.replace('–', '-').replace('—', '-')
    parts = [p.strip() for p in dates_str.split('-')]
    
    if len(parts) < 2:
        return None, None
    
    start_str = parts[0].strip()
    end_str = parts[1].strip()
    
    start_date = _parse_single_date(start_str)
    end_date = _parse_single_date(end_str) if end_str.lower() != 'present' else None
    
    return start_date, end_date


# ==========================================
# Helper Function: Parse Single Date
# ==========================================
def _parse_single_date(date_str):
    """
    Parse date string like "Sep. 2017" or "September 2017"
    Returns date string in 'YYYY-MM-DD' format or None
    """
    if not date_str:
        return None
    
    month_map = {
        'jan': '01', 'january': '01',
        'feb': '02', 'february': '02',
        'mar': '03', 'march': '03',
        'apr': '04', 'april': '04',
        'may': '05',
        'jun': '06', 'june': '06',
        'jul': '07', 'july': '07',
        'aug': '08', 'august': '08',
        'sep': '09', 'september': '09',
        'oct': '10', 'october': '10',
        'nov': '11', 'november': '11',
        'dec': '12', 'december': '12'
    }
    
    try:
        # Remove periods and split
        date_str = date_str.replace('.', '').strip()
        parts = date_str.split()
        
        if len(parts) >= 2:
            month_str = parts[0].lower()
            year_str = parts[1]
            
            if month_str in month_map and year_str.isdigit():
                month = month_map[month_str]
                year = year_str
                return f"{year}-{month}-01"
    except:
        pass
    
    return None