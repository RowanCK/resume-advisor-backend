"""
Health Check Endpoint
Provides server and database health status.
"""

from flask import Blueprint, jsonify, current_app
from ..utils import get_db

# ==========================================
# Blueprint setup
# ==========================================
health_bp = Blueprint('health', __name__, url_prefix='/health')

# ==========================================
# Routes
# ==========================================
@health_bp.route('', methods=['GET'])
def health_check():
    """
    Health Check
    Check API server and database connectivity status
    ---
    tags:
      - System
    responses:
      200:
        description: Health check result
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            status:
              type: string
              example: ok
            server:
              type: string
              example: running
            database:
              type: string
              enum: [connected, unavailable]
              example: connected
    """
    db_status = "unavailable"
    
    try:
        # Check database connection
        mysql = get_db()
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        db_status = "connected"
    except Exception as e:
        current_app.logger.error(f"Database health check failed: {str(e)}")

    return jsonify({
        "success": True,
        "status": "ok",
        "server": "running",
        "database": db_status
    }), 200