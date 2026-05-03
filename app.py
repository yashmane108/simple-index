from flask import Flask, render_template_string, request, redirect
import pymysql
import os
import boto3

app = Flask(__name__)

# Fetch environment variables from K8s
DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_NAME = os.environ.get('DB_NAME', 'devops_db') # Default to your new DB
REGION = "us-east-1"

def get_conn():
    # Generate the IAM Token dynamically for every connection
    rds_client = boto3.client('rds', region_name=REGION)
    token = rds_client.generate_db_auth_token(
        DBHostname=DB_HOST, 
        Port=3306, 
        DBUsername=DB_USER,
        Region=REGION
    )
    
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,      # Ensure this is "admin"
        password=token, # Your new master password
        database=DB_NAME,
        port=3306,
        ssl={'ca': 'global-bundle.pem'}, # Path to the file you downloaded
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5
    ) 

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Kubernetes Visitor Book</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 0; display: flex; flex-direction: column; align-items: center; }
        .header { background-color: #1a73e8; color: white; width: 100%; text-align: center; padding: 1rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .container { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 8px 16px rgba(0,0,0,0.1); width: 90%; max-width: 600px; margin-top: 2rem; }
        .tech-stack { background: #e8f0fe; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; text-align: left; }
        .tech-stack ul { list-style-type: none; padding: 0; margin: 0; }
        .tech-stack li { color: #1967d2; font-weight: bold; margin-bottom: 5px; }
        input, textarea { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        button { background-color: #34a853; color: white; border: none; padding: 12px 20px; border-radius: 4px; cursor: pointer; width: 100%; font-size: 1rem; }
        button:hover { background-color: #2d8e47; }
        .visitor-card { border-left: 5px solid #1a73e8; background: #fafafa; padding: 10px; margin-top: 10px; border-radius: 4px; text-align: left; }
        .status { font-weight: bold; color: {{ status_color }}; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Cloud-Native Visitor Book</h1>
    </div>
    <div class="container">
        <div class="tech-stack">
            <h3>🚀 Tech Stack Deployed:</h3>
            <ul>
                <li>🐳 Docker</li>
                <li>☸️ EKS (AWS Managed K8s)</li>
                <li>🤖 Jenkins (IAM IRSA Integration)</li>
                <li>☁️ AWS: EC2, RDS (IAM Auth Enabled)</li>
            </ul>
        </div>
        <p>Database Status: <span class="status">{{ db_status }}</span></p>
        <form method="POST">
            <input type="text" name="visitor_name" placeholder="Your Name" required>
            <textarea name="message" placeholder="Your Message" rows="3"></textarea>
            <button type="submit">Submit to RDS</button>
        </form>
        <hr>
        <h3>Recent Visitors:</h3>
        {% for entry in entries %}
        <div class="visitor-card">
            <strong>{{ entry.name }}</strong>: {{ entry.message }} <br>
            <small style="color: #888;">{{ entry.visit_time }}</small>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

@app.route('/debug')
def debug():
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        return str(identity)
    except Exception as e:
        return str(e)

@app.route('/health')
def health():
    return "OK", 200

@app.route('/', methods=['GET', 'POST'])
def index():
    db_status = "Disconnected ❌"
    visitors = []

    try:
        # 1. Always check connection for the status indicator
        conn = get_conn()
        db_status = "Connected ✅"
        
        # 2. Handle Data Submission (POST)
        if request.method == 'POST':
            name = request.form.get('name')
            message = request.form.get('message')
            if name and message:
                with conn.cursor() as cursor:
                    sql = "INSERT INTO visitors (name, message) VALUES (%s, %s)"
                    cursor.execute(sql, (name, message))
                conn.commit()
                # Redirect to clear the form and show the new entry
                return redirect('/')

        # 3. Fetch visitors for the list (GET or after POST)
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM visitors ORDER BY visit_time DESC")
            visitors = cursor.fetchall()
        conn.close()

    except Exception as e:
        db_status = f"Error: {str(e)} ❌"

    # 4. Pass db_status and visitors to your template
    return render_template_string(HTML_TEMPLATE, db_status=db_status, visitors=visitors)

if __name__ == "__main_
    app.run(host='0.0.0.0', port=80)
