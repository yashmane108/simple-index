import boto3
import pymysql
import os
from flask import Flask, render_template_string, request, redirect

app = Flask(__name__)

def get_conn():
    host = os.environ.get('DB_HOST')
    user = os.environ.get('DB_USER')
    region = "us-east-1"
    
    # Generate the IAM Token
    client = boto3.client('rds', region_name=region)
    token = client.generate_db_auth_token(DBHostname=host, Port=3306, DBUsername=user)
    
    return pymysql.connect(
        host=host,
        user=user,
        password=token, # Use token instead of static password
        database=os.environ.get('DB_NAME'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    ) 

# --- IMPROVED UI TEMPLATE ---
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
                <li>☸️ K8s (Ingress Controller)</li>
                <li>🤖 Jenkins (Shared Lib, Env, WebHooks)</li>
                <li>☁️ AWS: EC2, RDS</li>
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
        except:
            pass
        return redirect('/')

    entries = []
    try:
        conn = get_conn()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT name, message, visit_time FROM visitors ORDER BY id DESC LIMIT 5")
            entries = cursor.fetchall()
        conn.close()
    except Exception as e:
        db_status = f"Disconnected ❌ ({str(e)})"
        status_color = "#ea4335"

    return render_template_string(HTML_TEMPLATE, entries=entries, db_status=db_status, status_color=status_color)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)




def get_conn():
    return pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get data from the form
        visitor_name = request.form.get('visitor_name')
        msg = request.form.get('message')
        
        # Save to RDS
        conn = get_conn()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO visitors (name, message) VALUES (%s, %s)", (visitor_name, msg))
        conn.commit()
        conn.close()
        return redirect('/')

    # GET logic: Fetch last 5 visitors
    entries = []
    db_status = "Connected ✅"
    try:
        conn = get_conn()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT name, message, visit_time FROM visitors ORDER BY id DESC LIMIT 5")
            entries = cursor.fetchall()
        conn.close()
    except Exception as e:
        db_status = f"Connection Error ❌"

    # Minimal HTML with a form
    return f"""
    <html>
        <body style="font-family:sans-serif; text-align:center;">
            <h1>Kubernetes Visitor Book</h1>
            <p>Database: {db_status}</p>
            <form method="POST" style="margin-bottom:20px;">
                <input type="text" name="visitor_name" placeholder="Your Name" required><br><br>
                <textarea name="message" placeholder="Your Message"></textarea><br><br>
                <button type="submit">Submit to RDS</button>
            </form>
            <h3>Recent Visitors:</h3>
            <ul>
                {"".join([f"<li>{e['name']}: {e['message']} ({e['visit_time']})</li>" for e in entries])}
            </ul>
        </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
