# app.py
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import os

app = Flask(__name__)

# --------------------
# Database Configuration
# --------------------
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'password')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'resume_advisor')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# --------------------
# Routes / API Endpoints
# --------------------

# Health check
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'OK'}), 200

# Get all users
@app.route('/api/users', methods=['GET'])
def get_users():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    cur.close()
    return jsonify(users)

# Create a new user
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.json
    name = data.get('name')
    email = data.get('email')

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'User created successfully'}), 201

# Placeholder for LLM analysis of resume vs job description
@app.route('/api/analyze', methods=['POST'])
def analyze_resume():
    data = request.json
    resume_text = data.get('resume')
    job_description = data.get('job_description')

    # TODO: Integrate LLM to process resume and job description
    # Example: call LLM API, extract key skills, generate recommendations
    analysis_result = {
        "matched_skills": ["Python", "SQL"],  # example placeholder
        "recommendations": ["Highlight Python projects", "Include SQL experience"]
    }

    return jsonify(analysis_result)

# --------------------
# Main
# --------------------
if __name__ == '__main__':
    app.run(debug=True)
