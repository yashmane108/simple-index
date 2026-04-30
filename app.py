from flask import Flask
import pymysql
import os

app = Flask(__name__)

# These variable names MUST match your Deployment 'env' section
DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME')

@app.route('/')
def index():
    db_status = "Checking..."
    try:
        # Using the variables injected by K8s
        conn = pymysql.connect(
            host=DB_HOST, 
            user=DB_USER, 
            password=DB_PASS, 
            database=DB_NAME,
            connect_timeout=5
        )
        db_status = "Connected to AWS RDS! ✅"
        conn.close()
    except Exception as e:
        db_status = f"RDS Connection Failed ❌: {str(e)}"

    # Read your index.html
    try:
        with open('index.html', 'r') as f:
            html_content = f.read()
        # Inject status into your welcome message
        return html_content.replace('Welcome to Kubernetes!!!!!', f'Welcome! {db_status}')
    except:
        return f"<h1>Python App Running</h1><p>Status: {db_status}</p>"

if __name__ == "__main__":
    # Must be 0.0.0.0 to be accessible outside the container
    app.run(host='0.0.0.0', port=80)
