from flask import Flask, redirect, url_for, session, request, jsonify
import os
import requests

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_secret_key')

GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID', 'your_client_id')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET', 'your_client_secret')
GITHUB_AUTH_URL = 'https://github.com/login/oauth/authorize'
GITHUB_TOKEN_URL = 'https://github.com/login/oauth/access_token'
GITHUB_USER_API = 'https://api.github.com/user'

@app.route('/')
def index():
    user = session.get('user')
    if user:
        return f"<h2>Welcome, {user['login']}!</h2><br><a href='/logout'>Logout</a>"
    return "<a href='/login'>Login with GitHub</a>"

@app.route('/login')
def login():
    return redirect(f"{GITHUB_AUTH_URL}?client_id={GITHUB_CLIENT_ID}&scope=read:user")

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return 'No code provided', 400
    # Exchange code for access token
    token_resp = requests.post(
        GITHUB_TOKEN_URL,
        headers={'Accept': 'application/json'},
        data={
            'client_id': GITHUB_CLIENT_ID,
            'client_secret': GITHUB_CLIENT_SECRET,
            'code': code
        }
    )
    token_json = token_resp.json()
    access_token = token_json.get('access_token')
    if not access_token:
        return 'Failed to get access token', 400
    # Get user info
    user_resp = requests.get(
        GITHUB_USER_API,
        headers={'Authorization': f'token {access_token}'}
    )
    user_json = user_resp.json()
    session['user'] = user_json
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
