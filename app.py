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
    client = boto3.client('rds', region_name=REGION)
    token = client.generate_db_auth_token(DBHostname=DB_HOST, Port=3306, DBUsername=DB_USER)
    
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=token, # Use the dynamic IAM token
        database=DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
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

@app.route('/', methods=['GET', 'POST'])
def index():
    db_status = "Connected ✅"
    status_color = "#34a853"
    
    if request.method == 'POST':
        try:
            conn = get_conn()
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO visitors (name, message) VALUES (%s, %s)", 
                               (request.form.get('visitor_name'), request.form.get('message')))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving: {e}")
        return redirect('/')

    entries = []
    try:
        conn = get_conn()
        with conn.cursor() as cursor:
            cursor.execute("SELECT name, message, visit_time FROM visitors ORDER BY id DESC LIMIT 5")
            entries = cursor.fetchall()
        conn.close()
    except Exception as e:
        db_status = f"Disconnected ❌ ({str(e)})"
        status_color = "#ea4335"

    return render_template_string(HTML_TEMPLATE, entries=entries, db_status=db_status, status_color=status_color)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
