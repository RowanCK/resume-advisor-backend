"""
Main API Routes
Registers all endpoint blueprints.
"""

from flask import Blueprint
from .endpoints import (
    health_bp,
    auth_bp,
    users_bp,
    resumes_bp,
    cover_letters_bp,
    job_postings_bp,
    ai_bp
)

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Register all sub-blueprints
api_bp.register_blueprint(health_bp)
api_bp.register_blueprint(auth_bp)
api_bp.register_blueprint(users_bp)
api_bp.register_blueprint(resumes_bp)
api_bp.register_blueprint(cover_letters_bp)
api_bp.register_blueprint(job_postings_bp)
api_bp.register_blueprint(ai_bp)
