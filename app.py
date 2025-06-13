from flask import Flask, redirect, url_for, session, request, jsonify, render_template, flash
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
        return f"<h2>Welcome, {user['login']}!</h2><br><a href='/profile'>View Profile</a><br><a href='/logout'>Logout</a>"
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
    session['access_token'] = access_token  # Store the access token in session
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    # Check if user is logged in
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Get access token from session
    access_token = session.get('access_token')
    if not access_token:
        return redirect(url_for('login'))
    
    # Fetch detailed user information from GitHub API
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    user_response = requests.get('https://api.github.com/user', headers=headers)
    
    if user_response.status_code == 200:
        user_data = user_response.json()
        
        # Extract relevant user information
        user_info = {
            'login': user_data.get('login'),
            'name': user_data.get('name'),
            'email': user_data.get('email'),
            'avatar_url': user_data.get('avatar_url'),
            'bio': user_data.get('bio'),
            'location': user_data.get('location'),
            'company': user_data.get('company'),
            'blog': user_data.get('blog'),
            'twitter_username': user_data.get('twitter_username'),
            'public_repos': user_data.get('public_repos'),
            'followers': user_data.get('followers'),
            'following': user_data.get('following'),
            'created_at': user_data.get('created_at'),
            'updated_at': user_data.get('updated_at'),
            'html_url': user_data.get('html_url')
        }
        
        # For now, return a simple HTML response since profile.html doesn't exist yet
        return f"""
        <h1>GitHub Profile</h1>
        <img src="{user_info['avatar_url']}" width="100" height="100"><br>
        <h2>{user_info['name'] or user_info['login']}</h2>
        <p>Username: {user_info['login']}</p>
        <p>Email: {user_info['email'] or 'Not public'}</p>
        <p>Bio: {user_info['bio'] or 'No bio'}</p>
        <p>Location: {user_info['location'] or 'Not specified'}</p>
        <p>Company: {user_info['company'] or 'Not specified'}</p>
        <p>Public Repos: {user_info['public_repos']}</p>
        <p>Followers: {user_info['followers']}</p>
        <p>Following: {user_info['following']}</p>
        <p><a href="{user_info['html_url']}" target="_blank">View on GitHub</a></p>
        <br>
        <a href="/">Back to Home</a>
        """
    else:
        return f'Failed to fetch user information from GitHub. Status: {user_response.status_code}', 500

if __name__ == '__main__':
    app.run(debug=True)
