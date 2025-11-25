"""
AI Endpoints
Handles AI-powered features including job analysis, resume suggestions, and cover letter generation
"""

from flask import Blueprint, request
from ..auth_utils import handle_errors,require_auth
from ..utils import success_response, error_response, validate_required_fields
from ..ai_client import get_ai_client

ai_bp = Blueprint('ai', __name__)


# ==========================================
# Analyze Job Description
# ==========================================
@ai_bp.route('/analyze-job', methods=['POST'])
@handle_errors
@require_auth
def analyze_job_description(auth_user_id):
    """
    Analyze a job description and extract structured keywords
    ---
    tags:
      - AI
    summary: Extract keywords and requirements from job posting text
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        description: Job description to analyze
        schema:
          type: object
          required:
            - job_description
          properties:
            job_description:
              type: string
              example: "We are seeking a Senior Software Engineer with 5+ years of experience in Python, AWS, and Docker..."
    responses:
      200:
        description: Job posting information extracted successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                title:
                  type: string
                  example: "Senior Software Engineer"
                company_name:
                  type: string
                  example: "Google"
                company_location:
                  type: string
                  example: "Mountain View, CA"
                company_industry:
                  type: string
                  example: "Technology"
                company_website:
                  type: string
                  example: "https://www.google.com"
                description:
                  type: string
                  example: "We are seeking an experienced software engineer to join our team and build scalable cloud solutions."
                job_location:
                  type: string
                  example: "Remote"
                posted_date:
                  type: string
                  example: "2025-11-01"
                close_date:
                  type: string
                  example: "2025-12-01"
                requirements:
                  type: array
                  items:
                    type: string
                  example: ["5+ years experience", "Python expertise", "Bachelor's degree"]
      400:
        description: Bad request - missing or invalid job description
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: "Missing required field job_description"
      401:
        description: Unauthorized - missing or invalid authentication token
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: "Authentication token required"
      500:
        description: Internal server error - AI service failure
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: Failed to analyze job description
    """
    data = request.get_json()
    
    # Validate required fields
    try:
        validate_required_fields(data, ['job_description'])
    except ValueError as e:
        return error_response(str(e), 400)
    
    job_text = data['job_description']
    
    # Validate job description is not empty
    if not job_text or not job_text.strip():
        return error_response('Job description cannot be empty', 400)
    
    # Check minimum length (at least 50 characters for meaningful analysis)
    if len(job_text.strip()) < 50:
        return error_response('Job description is too short. Please provide a more detailed description.', 400)
    
    try:
        # Get AI client and analyze job description
        ai_client = get_ai_client()
        job_data = ai_client.analyze_job_description(job_text)
        
        return success_response(job_data)
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Error analyzing job description: {str(e)}")
        return error_response('Failed to analyze job description. Please try again.', 500)