"""
Job Postings Endpoints
Handles job posting management and search
"""

from flask import Blueprint, request
from datetime import datetime
from ..auth_utils import require_auth, handle_errors
from ..utils import get_db, success_response, error_response, validate_required_fields

job_postings_bp = Blueprint('job_postings', __name__, url_prefix='/job-postings')

# ==========================================
# List All Job Postings
# ==========================================
@job_postings_bp.route('', methods=['GET'])
@handle_errors
def list_job_postings():
    """
    List all job postings with optional filters
    ---
    tags:
      - Job Postings
    summary: Retrieve all job postings with optional filtering
    security:
      - Bearer: []
    parameters:
      - name: company
        in: query
        type: string
        required: false
        description: Filter by company name
        example: Google
      - name: location
        in: query
        type: string
        required: false
        description: Filter by job location
        example: Calgary
      - name: limit
        in: query
        type: integer
        required: false
        description: Maximum number of results
        example: 10
    responses:
      200:
        description: Job postings retrieved successfully
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
                    example: Senior Software Engineer
                  company_name:
                    type: string
                    example: Google
                  company_location:
                    type: string
                    example: Mountain View, CA
                  job_location:
                    type: string
                    example: Remote
                  posted_date:
                    type: string
                    example: "2025-11-01"
                  close_date:
                    type: string
                    example: "2025-12-01"
    """
    company_filter = request.args.get('company')
    location_filter = request.args.get('location')
    limit = request.args.get('limit', 50, type=int)
    
    mysql = get_db()
    cursor = mysql.connection.cursor()
    
    query = """
        SELECT 
            jp.id,
            jp.title,
            jp.job_location,
            DATE_FORMAT(jp.posted_date, '%%Y-%%m-%%d') as posted_date,
            DATE_FORMAT(jp.close_date, '%%Y-%%m-%%d') as close_date,
            c.name as company_name,
            c.location as company_location,
            c.industry as company_industry
        FROM job_postings jp
        JOIN company c ON jp.company_id = c.id
        WHERE 1=1
    """
    
    params = []
    
    if company_filter:
        query += " AND c.name LIKE %s"
        params.append(f"%{company_filter}%")
    
    if location_filter:
        query += " AND (jp.job_location LIKE %s OR c.location LIKE %s)"
        params.append(f"%{location_filter}%")
        params.append(f"%{location_filter}%")
    
    query += " ORDER BY jp.posted_date DESC LIMIT %s"
    params.append(limit)
    
    cursor.execute(query, tuple(params))
    job_postings = cursor.fetchall()
    cursor.close()
    
    return success_response({'data': job_postings})


# ==========================================
# Get Job Posting by ID
# ==========================================
@job_postings_bp.route('/<int:job_id>', methods=['GET'])
@handle_errors
def get_job_posting(job_id):
    """
    Get detailed job posting by ID
    ---
    tags:
      - Job Postings
    summary: Retrieve a specific job posting with full details
    security:
      - Bearer: []
    parameters:
      - name: job_id
        in: path
        type: integer
        required: true
        description: The ID of the job posting
        example: 201
    responses:
      200:
        description: Job posting retrieved successfully
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
                  example: 201
                title:
                  type: string
                  example: Senior Software Engineer
                description:
                  type: string
                  example: We are seeking an experienced software engineer...
                job_location:
                  type: string
                  example: Remote
                posted_date:
                  type: string
                  example: "2025-11-01"
                close_date:
                  type: string
                  example: "2025-12-01"
                company:
                  type: object
                  properties:
                    id:
                      type: integer
                      example: 101
                    name:
                      type: string
                      example: Google
                    location:
                      type: string
                      example: Mountain View, CA
                    industry:
                      type: string
                      example: Technology
                    website:
                      type: string
                      example: https://www.google.com
                requirements:
                  type: array
                  items:
                    type: string
                  example: ["5+ years experience", "Python expertise", "Bachelor's degree"]
      404:
        description: Job posting not found
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: Job posting not found
    """
    mysql = get_db()
    cursor = mysql.connection.cursor()
    
    # Get job posting details
    cursor.execute("""
        SELECT 
            jp.id,
            jp.title,
            jp.description,
            jp.job_location,
            DATE_FORMAT(jp.posted_date, '%%Y-%%m-%%d') as posted_date,
            DATE_FORMAT(jp.close_date, '%%Y-%%m-%%d') as close_date,
            c.id as company_id,
            c.name as company_name,
            c.location as company_location,
            c.industry as company_industry,
            c.website as company_website
        FROM job_postings jp
        JOIN company c ON jp.company_id = c.id
        WHERE jp.id = %s
    """, (job_id,))
    
    job = cursor.fetchone()
    
    if not job:
        cursor.close()
        return error_response('Job posting not found', 404)
    
    # Get job requirements
    cursor.execute("""
        SELECT requirement
        FROM job_requirements
        WHERE job_id = %s
    """, (job_id,))
    
    requirements = [row['requirement'] for row in cursor.fetchall()]
    cursor.close()
    
    # Build response
    response_data = {
        'id': job['id'],
        'title': job['title'],
        'description': job['description'],
        'job_location': job['job_location'],
        'posted_date': job['posted_date'],
        'close_date': job['close_date'],
        'company': {
            'id': job['company_id'],
            'name': job['company_name'],
            'location': job['company_location'],
            'industry': job['company_industry'],
            'website': job['company_website']
        },
        'requirements': requirements
    }
    
    return success_response({'data': response_data})


# ==========================================
# Create Job Posting
# ==========================================
@job_postings_bp.route('', methods=['POST'])
@handle_errors
@require_auth
def create_job_posting(auth_user_id):
    """
    Create a new job posting
    ---
    tags:
      - Job Postings
    summary: Create a new job posting (admin/recruiter only)
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        description: Job posting data
        schema:
          type: object
          required:
            - title
            - company_name
            - job_location
          properties:
            title:
              type: string
              example: Senior Software Engineer
            company_name:
              type: string
              example: Google
            company_location:
              type: string
              example: Mountain View, CA
            company_industry:
              type: string
              example: Technology
            company_website:
              type: string
              example: https://www.google.com
            description:
              type: string
              example: We are seeking an experienced software engineer...
            job_location:
              type: string
              example: Remote
            posted_date:
              type: string
              format: date
              example: "2025-11-01"
            close_date:
              type: string
              format: date
              example: "2025-12-01"
            requirements:
              type: array
              items:
                type: string
              example: ["5+ years experience", "Python expertise", "Bachelor's degree"]
    security:
      - Bearer: []
    responses:
      201:
        description: Job posting created successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            job_id:
              type: integer
              example: 201
            message:
              type: string
              example: Job posting created successfully
      400:
        description: Bad request
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: Missing required field
    """
    data = request.get_json()
    
    # Validate required fields
    try:
        validate_required_fields(data, ['title', 'company_name', 'job_location'])
    except ValueError as e:
        return error_response(str(e), 400)
    
    mysql = get_db()
    cursor = mysql.connection.cursor()
    
    # Check if company exists, if not create it
    cursor.execute("SELECT id FROM company WHERE name = %s", (data['company_name'],))
    company = cursor.fetchone()
    
    if company:
        company_id = company['id']
    else:
        # Create new company
        cursor.execute("""
            INSERT INTO company (name, location, industry, website)
            VALUES (%s, %s, %s, %s)
        """, (
            data['company_name'],
            data.get('company_location'),
            data.get('company_industry'),
            data.get('company_website')
        ))
        company_id = cursor.lastrowid
    
    # Create job posting
    posted_date = data.get('posted_date', datetime.now().strftime('%Y-%m-%d'))
    close_date = data.get('close_date')
    
    cursor.execute("""
        INSERT INTO job_postings (title, company_id, description, job_location, posted_date, close_date)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        data['title'],
        company_id,
        data.get('description'),
        data['job_location'],
        posted_date,
        close_date
    ))
    
    job_id = cursor.lastrowid
    
    # Add requirements if provided
    requirements = data.get('requirements', [])
    for req in requirements:
        cursor.execute("""
            INSERT INTO job_requirements (job_id, requirement)
            VALUES (%s, %s)
        """, (job_id, req))
    
    mysql.connection.commit()
    cursor.close()
    
    return success_response({
        'job_id': job_id,
        'message': 'Job posting created successfully'
    }, 201)


# ==========================================
# Update Job Posting
# ==========================================
@job_postings_bp.route('/<int:job_id>', methods=['PUT'])
@handle_errors
@require_auth
def update_job_posting(auth_user_id, job_id):
    """
    Update an existing job posting
    ---
    tags:
      - Job Postings
    summary: Update a job posting (admin/recruiter only)
    security:
      - Bearer: []
    parameters:
      - name: job_id
        in: path
        type: integer
        required: true
        description: The ID of the job posting to update
        example: 201
      - name: body
        in: body
        required: true
        description: Updated job posting data
        schema:
          type: object
          properties:
            title:
              type: string
              example: Senior Software Engineer
            description:
              type: string
              example: Updated job description
            job_location:
              type: string
              example: Remote
            close_date:
              type: string
              format: date
              example: "2025-12-15"
            requirements:
              type: array
              items:
                type: string
              example: ["5+ years experience", "Python expertise"]
    security:
      - Bearer: []
    responses:
      200:
        description: Job posting updated successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: Job posting updated successfully
      404:
        description: Job posting not found
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: Job posting not found
    """
    data = request.get_json()
    
    mysql = get_db()
    cursor = mysql.connection.cursor()
    
    # Check if job exists
    cursor.execute("SELECT id FROM job_postings WHERE id = %s", (job_id,))
    if not cursor.fetchone():
        cursor.close()
        return error_response('Job posting not found', 404)
    
    # Build update query dynamically
    update_fields = []
    params = []
    
    if 'title' in data:
        update_fields.append("title = %s")
        params.append(data['title'])
    
    if 'description' in data:
        update_fields.append("description = %s")
        params.append(data['description'])
    
    if 'job_location' in data:
        update_fields.append("job_location = %s")
        params.append(data['job_location'])
    
    if 'close_date' in data:
        update_fields.append("close_date = %s")
        params.append(data['close_date'])
    
    if update_fields:
        query = f"UPDATE job_postings SET {', '.join(update_fields)} WHERE id = %s"
        params.append(job_id)
        cursor.execute(query, tuple(params))
    
    # Update requirements if provided
    if 'requirements' in data:
        # Delete existing requirements
        cursor.execute("DELETE FROM job_requirements WHERE job_id = %s", (job_id,))
        
        # Insert new requirements
        for req in data['requirements']:
            cursor.execute("""
                INSERT INTO job_requirements (job_id, requirement)
                VALUES (%s, %s)
            """, (job_id, req))
    
    mysql.connection.commit()
    cursor.close()
    
    return success_response({'message': 'Job posting updated successfully'})


# ==========================================
# Delete Job Posting
# ==========================================
@job_postings_bp.route('/<int:job_id>', methods=['DELETE'])
@handle_errors
@require_auth
def delete_job_posting(auth_user_id, job_id):
    """
    Delete a job posting
    ---
    tags:
      - Job Postings
    summary: Delete a job posting (admin only)
    security:
      - Bearer: []
    parameters:
      - name: job_id
        in: path
        type: integer
        required: true
        description: The ID of the job posting to delete
        example: 201
    security:
      - Bearer: []
    responses:
      200:
        description: Job posting deleted successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: Job posting deleted successfully
      404:
        description: Job posting not found
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: Job posting not found
    """
    mysql = get_db()
    cursor = mysql.connection.cursor()
    
    # Check if job exists
    cursor.execute("SELECT id FROM job_postings WHERE id = %s", (job_id,))
    if not cursor.fetchone():
        cursor.close()
        return error_response('Job posting not found', 404)
    
    # Delete job posting (requirements will be deleted by CASCADE)
    cursor.execute("DELETE FROM job_postings WHERE id = %s", (job_id,))
    mysql.connection.commit()
    cursor.close()
    
    return success_response({'message': 'Job posting deleted successfully'})


# ==========================================
# Search Job Postings
# ==========================================
@job_postings_bp.route('/search', methods=['GET'])
@handle_errors
def search_job_postings():
    """
    Search job postings by keywords
    ---
    tags:
      - Job Postings
    summary: Search job postings by title, description, or requirements
    security:
      - Bearer: []
    parameters:
      - name: q
        in: query
        type: string
        required: true
        description: Search keyword
        example: python developer
      - name: limit
        in: query
        type: integer
        required: false
        description: Maximum number of results
        example: 20
    responses:
      200:
        description: Search results
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
      400:
        description: Missing search query
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: Search query is required
    """
    query = request.args.get('q')
    limit = request.args.get('limit', 20, type=int)
    
    if not query:
        return error_response('Search query is required', 400)
    
    mysql = get_db()
    cursor = mysql.connection.cursor()
    
    search_pattern = f"%{query}%"
    
    cursor.execute("""
        SELECT DISTINCT
            jp.id,
            jp.title,
            jp.job_location,
            DATE_FORMAT(jp.posted_date, '%%Y-%%m-%%d') as posted_date,
            c.name as company_name,
            c.location as company_location
        FROM job_postings jp
        JOIN company c ON jp.company_id = c.id
        LEFT JOIN job_requirements jr ON jp.id = jr.job_id
        WHERE jp.title LIKE %s 
           OR jp.description LIKE %s
           OR jr.requirement LIKE %s
        ORDER BY posted_date DESC
        LIMIT %s
    """, (search_pattern, search_pattern, search_pattern, limit))
    
    results = cursor.fetchall()
    cursor.close()
    
    return success_response({'data': results})
