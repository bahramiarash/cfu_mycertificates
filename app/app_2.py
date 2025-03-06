from flask import Flask, redirect, url_for, session, jsonify, send_file
from authlib.integrations.flask_client import OAuth
import os
import io
import MySQLdb

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your_secret_key")


# SSO Configuration
SSO_CLIENT_ID = "your_client_id"
SSO_CLIENT_SECRET = "your_client_secret"
SSO_AUTH_URL = "https://sso.example.com/auth"
SSO_TOKEN_URL = "https://sso.example.com/token"
SSO_USERINFO_URL = "https://sso.example.com/userinfo"

oauth = OAuth(app)
sso = oauth.register(
    name="sso",
    client_id=SSO_CLIENT_ID,
    client_secret=SSO_CLIENT_SECRET,
    authorize_url=SSO_AUTH_URL,
    access_token_url=SSO_TOKEN_URL,
    userinfo_endpoint=SSO_USERINFO_URL,
    client_kwargs={"scope": "openid profile email"},
)

# Database connection
DB_HOST = os.getenv('DB_HOST', 'mariadb')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '12#qwEasDzxC')
DB_NAME = os.getenv('DB_NAME', 'cert_db')

db = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME)
cursor = db.cursor()

@app.route("/")
def home():
    user = session.get("user")
    if user:
        return f"Welcome, {user.get('name', 'Unknown User')}! <a href='/certificates'>View Certificates</a>"
    return '<a href="/login">Login with SSO</a>'

@app.route("/login")
def login():
    return sso.authorize_redirect(redirect_uri=url_for("callback", _external=True))

@app.route("/callback")
def callback():
    token = sso.authorize_access_token()
    user_info = sso.userinfo(token=token)
    # Store entire user_info or just the sub/national_id
    session["user"] = user_info
    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

@app.route("/certificates", methods=["GET"])
def list_certificates():
    user = session.get("user")
    # if not user:
    #     return redirect(url_for("login"))
    
    # Suppose SSO "sub" maps to 'national_id'
    national_id = 1234567890 #user.get("sub")  # or user["national_id"], depending on your SSO claim
    if not national_id:
        return "No national_id found in user info", 400
    
    # Query certificates
    cursor.execute("""
        SELECT c.id, c.cert_name 
        FROM certificates c
        JOIN users u ON c.user_id = u.id
        WHERE u.national_id = %s
    """, (national_id,))
    certs = cursor.fetchall()
    return jsonify([{"cert_id": c[0], "cert_name": c[1]} for c in certs])

@app.route("/certificate/<int:cert_id>", methods=["GET"])
def get_certificate(cert_id):
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))

    # Check if cert_id belongs to this user
    # national_id = user.get("sub")
    national_id = 1234567890
    cursor.execute("""
        SELECT c.cert_file, c.cert_name
        FROM certificates c
        JOIN users u ON c.user_id = u.id
        WHERE c.id = %s AND u.national_id = %s
    """, (cert_id, national_id))
    cert = cursor.fetchone()
    if cert:
        return send_file(io.BytesIO(cert[0]), mimetype="image/svg+xml", as_attachment=True, download_name=f"{cert[1]}.svg")
    return jsonify({"error": "Certificate not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
