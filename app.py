from flask import Flask, render_template_string, request, redirect
import pymysql
import os

app = Flask(__name__)

# Config from K8s Secrets
DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME', 'devops_db') # Default to your new DB

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
