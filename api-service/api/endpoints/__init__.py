"""
API Endpoints Package
Includes route blueprints for different resources.
"""

from .health import health_bp
from .auth import auth_bp
from .user import user_bp
from .resumes import resumes_bp
from .cover_letters import cover_letters_bp
from .job_postings import job_postings_bp
from .ai import ai_bp

# Collect all blueprints here
__all__ = [
    'health_bp',
    'auth_bp',
    'user_bp',
    'resumes_bp',
    'cover_letters_bp',
    'job_postings_bp',
    'ai_bp'
]
