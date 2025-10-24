import os
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# --------------------
# Database Configuration
# --------------------
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'mysql')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'user')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'password')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'resume_advisor')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# --------------------
# Routes / API Endpoints
# --------------------
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'OK'}), 200

# --------------------
# Main
# --------------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=6666, debug=True, use_reloader=True)
