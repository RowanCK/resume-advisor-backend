"""
Resume Advisor API
Main application entry point
"""

import os
from flask import Flask, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS

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
    
    # Make mysql accessible to blueprints
    app.mysql = mysql
    
    # Register blueprints
    from api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
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
    
    # Get configuration from environment
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 6666))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"Starting Resume Advisor API on {host}:{port}")
    print(f"Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug)

