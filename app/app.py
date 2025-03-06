from flask import Flask, session, redirect, url_for, jsonify, send_file, render_template, Response
from authlib.integrations.flask_client import OAuth
import os
import io
import MySQLdb

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "replace_me")

# SSO Config
SSO_CLIENT_ID = os.getenv("SSO_CLIENT_ID", "bicfu")
SSO_CLIENT_SECRET = os.getenv("SSO_CLIENT_SECRET", "5r75G@t39!")
SSO_AUTH_URL = "https://sso.cfu.ac.ir/auth"
SSO_TOKEN_URL = "https://sso.cfu.ac.ir/token"
SSO_USERINFO_URL = "https://sso.cfu.ac.ir/userinfo"

oauth = OAuth(app)
sso = oauth.register(
    name="sso",
    client_id=SSO_CLIENT_ID,
    client_secret=SSO_CLIENT_SECRET,
    authorize_url=SSO_AUTH_URL,
    access_token_url=SSO_TOKEN_URL,
    userinfo_endpoint=SSO_USERINFO_URL,
    client_kwargs={"scope": "openid profile"},
)

# Database Config
DB_HOST = os.getenv("DB_HOST", "mariadb")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "12#qwEasDzxC")
DB_NAME = os.getenv("DB_NAME", "cert_db")

# Create a global DB connection at import time (simple approach)
db = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME)
cursor = db.cursor()

@app.route("/")
def home():
    user = session.get("user")
    if user:
        return f"Welcome, {user.get('name', 'User')}! <a href='/certificates'>View Certificates</a>"
    return '<a href="/login">Login with SSO</a>'

@app.route("/login")
def login():
    return sso.authorize_redirect(redirect_uri=url_for("callback", _external=True))

@app.route("/callback")
def callback():
    token = sso.authorize_access_token()
    user_info = sso.userinfo(token=token)
    session["user"] = user_info
    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

@app.route("/certificates")
def list_certificates():
    # user = session.get("user")
    # if not user:
    #     return redirect(url_for("login"))

    # Suppose the SSO "sub" or "email" maps to the user’s national_id in DB
    national_id = 1234567890 #user.get("sub") or user.get("email")
    if not national_id:
        return "No national_id or sub in user_info", 400

    cursor.execute("""
        SELECT c.id, c.cert_name
        FROM certificates c
        JOIN users u ON c.user_id = u.id
        WHERE u.national_id = %s
    """, (national_id,))
    rows = cursor.fetchall()

    # Return JSON
    # return jsonify([{"cert_id": r[0], "cert_name": r[1]} for r in rows])
    return render_template("certificates.html", certificates=rows)

# @app.route("/certificate/<int:cert_id>")
# def get_certificate(cert_id):
#     # user = session.get("user")
#     # if not user:
#     #     return redirect(url_for("login"))

#     national_id = 1234567890 #user.get("sub") or user.get("email")
#     cursor.execute("""
#         SELECT c.cert_file, c.cert_name
#         FROM certificates c
#         JOIN users u ON c.user_id = u.id
#         WHERE c.id = %s AND u.national_id = %s
#     """, (cert_id, national_id))
#     row = cursor.fetchone()

#     if row:
#         cert_file, cert_name = row
#         return send_file(io.BytesIO(cert_file), mimetype="image/svg+xml",
#                          as_attachment=True, download_name=f"{cert_name}.svg")
#     return jsonify({"error": "Not found or not yours"}), 404

@app.route("/certificate/<int:user_id>")
def show_certificate(user_id):
    # 1. Check if user is logged in (optional)
    # user_session = session.get("user")
    # if not user_session:
    #     return redirect(url_for("login"))  # or handle unauthorized access

    # 2. Get user's full name from DB
    cursor.execute("""
        SELECT fname, lname
        FROM users
        WHERE id = %s
    """, (user_id,))
    row = cursor.fetchone()
    if row:
        fname, lname = row
        user_name = f"{fname} {lname}"
    else:
        user_name = "Unknown User"

    # 3. Read the SVG template from disk
    svg_path = "./app/certs/cert1.svg"  # Adjust if needed
    with open(svg_path, "r", encoding="utf-8") as f:
        svg_content = f.read()

    # 4. Replace placeholder with the actual user name
    updated_svg = svg_content.replace("{{full_name}}", user_name)

    # 5. Serve the updated SVG as image/svg+xml
    return Response(updated_svg, mimetype="image/svg+xml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
