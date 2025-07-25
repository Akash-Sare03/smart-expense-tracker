# 📁 flask_auth/auth_server.py

from flask import Flask, redirect, request, session, url_for
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import os
import json

app = Flask(__name__)
app.secret_key = "c89f6d871f79a9e8b01c65b9abf99e55f9c261748f7c228327ca77a841e2d90c"  # Replace this with a secure random key

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # For development/testing only

# ✅ Load your client secrets
CLIENT_SECRETS_FILE = "credentials.json"
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

@app.route("/")
def index():
    return "✅ Auth server is running! Go to /login to authenticate with Google."

@app.route("/login")
def login():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('callback', _external=True)
    )
    auth_url, state = flow.authorization_url(prompt='consent', access_type='offline', include_granted_scopes='true')
    session["state"] = state
    return redirect(auth_url)

@app.route("/callback")
def callback():
    state = session["state"]
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=url_for('callback', _external=True)
    )
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    # ✅ Save credentials to file (shared with Streamlit)
    with open("token.json", "w") as token:
        json.dump(session['credentials'], token)

    return redirect("https://smart-expense-tracker-sldw.onrender.com")  # 🔁 Your Streamlit app link here

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

#if __name__ == "__main__":
   # port = int(os.environ.get("PORT", 5000))
   # app.run(host="0.0.0.0", port=port, debug=True)
