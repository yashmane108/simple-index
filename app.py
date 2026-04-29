from flask import Flask, render_template_string
import pymysql
import os

app = Flask(__name__)

# Get RDS details from K8s Secrets
DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME')

@app.route('/')
def index():
    db_status = "Checking..."
    try:
        # Try to connect to RDS
        conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME)
        db_status = "Connected to AWS RDS! ✅"
        conn.close()
    except Exception as e:
        db_status = f"RDS Connection Failed ❌"

    # Read your original index.html file
    with open('index.html', 'r') as f:
        html_content = f.read()
    
    # Inject the database status into your HTML
    # We replace a placeholder in your HTML with the actual status
    return html_content.replace('Welcome to Kubernetes!!!!!', f'Welcome! {db_status}')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
