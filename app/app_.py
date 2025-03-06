from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
import os

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
SSO_CLIENT_ID = "your_client_id"
SSO_CLIENT_SECRET = "your_client_secret"
SSO_AUTH_URL = "https://sso.example.com/auth"
SSO_TOKEN_URL = "https://sso.example.com/token"
SSO_USERINFO_URL = "https://sso.example.com/userinfo"

app = Flask(__name__)
app.secret_key = SECRET_KEY

oauth = OAuth(app)
sso = oauth.register(
    name="sso",
    client_id=SSO_CLIENT_ID,
    client_secret=SSO_CLIENT_SECRET,
    authorize_url=SSO_AUTH_URL,
    authorize_params=None,
    access_token_url=SSO_TOKEN_URL,
    access_token_params=None,
    userinfo_endpoint=SSO_USERINFO_URL,
    client_kwargs={"scope": "openid profile email"},
)

@app.route("/")
def home():
    user = session.get("user")
    if user:
        return f"Welcome, {user['name']}!"
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
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
