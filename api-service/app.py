"""
Resume Advisor API
Main application entry point
"""

import os
from flask import Flask, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from flasgger import Swagger

# --------------------
# App Factory
# --------------------
def create_app(config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('config.Config')
    if config:
        app.config.update(config)
    
    # Initialize extensions
    mysql = MySQL(app)
    CORS(app)  # Enable CORS for frontend
    
    # Initialize Swagger
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs",
        "url_prefix": None
    }
    
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Resume Advisor API",
            "description": "API for Resume Advisor Application",
            "version": "1.0.0",
            "contact": {
                "name": "API Support",
                "email": "support@resumeadvisor.com"
            }
        },
        "host": "localhost",
        "basePath": "/api/v1",
        "schemes": ["https", "http"],
        "securityDefinitions": {
            "bearerAuth": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Enter: Bearer {your token}"
            }
        }
    }
    
    Swagger(app, config=swagger_config, template=swagger_template)
    
    # Make mysql accessible to blueprints
    app.mysql = mysql
    
    # Register blueprints
    from api.routes import api_bp
    app.register_blueprint(api_bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app

# --------------------
# Error Handlers
# --------------------
def register_error_handlers(app):
    """Register global error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Resource not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle uncaught exceptions"""
        app.logger.error(f'Unhandled exception: {str(error)}')
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred'
        }), 500

# --------------------
# Main
# --------------------
if __name__ == '__main__':
    app = create_app()

    print("=" * 50)
    print("Resume Advisor Backend Server Starting...")
    print("=" * 50)
    
    # Get configuration from environment
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 8080))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"Starting Resume Advisor API on {host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"Swagger UI available at: http://{host}:{port}/api/docs")
    
    app.run(host=host, port=port, debug=debug)