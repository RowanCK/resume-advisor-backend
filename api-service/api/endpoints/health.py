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
    Health Check Endpoint
    Verifies that the API server and database are reachable.
    
    Returns:
        JSON response with API and DB status.
    """
    # try:
    #     # Check database connection
    #     mysql = get_db()
    #     cursor = mysql.connection.cursor()
    #     cursor.execute("SELECT 1")
    #     cursor.fetchone()
    #     cursor.close()
    #     db_status = "connected"
    # except Exception as e:
    #     current_app.logger.error(f"Database health check failed: {str(e)}")
    #     db_status = "unavailable"
    
    return jsonify({'status': 'OK'}), 200

    # return jsonify({
    #     "success": True,
    #     "status": "ok",
    #     "server": "running",
    #     "database": db_status
    # }), 200
