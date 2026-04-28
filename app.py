from flask import Flask
import pymysql
import os

app = Flask(__name__)

# Fetching Secrets from K8s Environment Variables
DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME')

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def home():
    status = "Testing..."
    try:
        conn = get_db_connection()
        status = "Connected to AWS RDS! ✅"
        conn.close()
    except Exception as e:
        status = f"Database Connection Failed ❌: {str(e)}"

    # This returns your HTML with the dynamic status
    return f"""
    <html>
        <head><title>K8s Python App</title></head>
        <body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
            <h1>Welcome to Kubernetes with Python!</h1>
            <div style="padding: 20px; border: 1px solid #ccc; display: inline-block;">
                <p><strong>Database Status:</strong> {status}</p>
            </div>
        </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
