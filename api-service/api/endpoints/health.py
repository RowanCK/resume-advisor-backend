"""
Health Check Endpoint
Provides server and database health status.
"""

from flask import Blueprint, jsonify, current_app
import MySQLdb

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
    error_msg = None
    
    try:
        # Try to get MySQL connection from Flask-MySQLdb
        mysql = current_app.mysql
        
        if mysql and mysql.connection:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            db_status = "connected"
            current_app.logger.info("Database health check passed")
        else:
            # Fallback: try direct connection
            current_app.logger.warning("Flask-MySQLdb connection is None, trying direct connection")
            conn = MySQLdb.connect(
                host=current_app.config['MYSQL_HOST'],
                user=current_app.config['MYSQL_USER'],
                password=current_app.config['MYSQL_PASSWORD'],
                database=current_app.config['MYSQL_DB']
            )
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            db_status = "connected"
            current_app.logger.info("Direct database connection successful")
            
    except Exception as e:
        current_app.logger.error(f"Database health check failed: {str(e)}")
        error_msg = str(e)
        db_status = "unavailable"

    response = {
        "success": True,
        "status": "ok",
        "server": "running",
        "database": db_status
    }

    if error_msg and current_app.config.get('DEBUG'):
        response["error"] = error_msg
    
    return jsonify(response), 200