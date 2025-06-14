from flask import Flask, redirect, url_for, session, request, jsonify
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_secret_key')

# Enable CORS for React frontend on port 80
CORS(app, supports_credentials=True, origins=['http://localhost', 'http://localhost:80', 'http://localhost:3000'])

GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID', 'your_client_id')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET', 'your_client_secret')
GITHUB_AUTH_URL = 'https://github.com/login/oauth/authorize'
GITHUB_TOKEN_URL = 'https://github.com/login/oauth/access_token'
GITHUB_USER_API = 'https://api.github.com/user'
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost')
BACKEND_PORT = int(os.environ.get('BACKEND_PORT', '5000'))
BACKEND_HOST = os.environ.get('BACKEND_HOST', 'localhost')
CALLBACK_URL = os.environ.get('CALLBACK_URL', f'http://{BACKEND_HOST}:{BACKEND_PORT}/api/callback')

@app.route('/api/user')
def get_user():
    user = session.get('user')
    if user:
        return jsonify({'authenticated': True, 'user': user})
    return jsonify({'authenticated': False}), 401

@app.route('/api/login')
def login():
    # Return the GitHub OAuth URL for the frontend to redirect to
    # The callback URL should point to the backend API
    callback_url = CALLBACK_URL
    return jsonify({
        'auth_url': f"{GITHUB_AUTH_URL}?client_id={GITHUB_CLIENT_ID}&scope=read:user&redirect_uri={callback_url}"
    })

@app.route('/api/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return redirect(f"{FRONTEND_URL}/login?error=no_code")
    
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
        return redirect(f"{FRONTEND_URL}/login?error=token_failed")
    
    # Get user info
    user_resp = requests.get(
        GITHUB_USER_API,
        headers={'Authorization': f'token {access_token}'}
    )
    user_json = user_resp.json()
    session['user'] = user_json
    session['access_token'] = access_token
    
    # Redirect to React app after successful authentication
    return redirect(f"{FRONTEND_URL}/")

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/api/profile')
def profile():
    # Check if user is logged in
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get access token from session
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({'error': 'No access token'}), 401
    
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
        
        return jsonify(user_info)
    else:
        return jsonify({'error': f'Failed to fetch user information from GitHub'}), user_response.status_code

@app.route('/api/repositories')
def repositories():
    # Check if user is logged in
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get access token from session
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({'error': 'No access token'}), 401
    
    # Fetch repositories from GitHub API
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Get repositories with pagination support
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 30, type=int)
    sort = request.args.get('sort', 'updated')  # updated, created, pushed, full_name
    
    repos_response = requests.get(
        f'https://api.github.com/user/repos?page={page}&per_page={per_page}&sort={sort}', 
        headers=headers
    )
    
    if repos_response.status_code == 200:
        repos_data = repos_response.json()
        
        # Extract relevant repository information
        repositories = []
        for repo in repos_data:
            repo_info = {
                'id': repo.get('id'),
                'name': repo.get('name'),
                'full_name': repo.get('full_name'),
                'description': repo.get('description'),
                'private': repo.get('private'),
                'html_url': repo.get('html_url'),
                'clone_url': repo.get('clone_url'),
                'ssh_url': repo.get('ssh_url'),
                'language': repo.get('language'),
                'stargazers_count': repo.get('stargazers_count'),
                'watchers_count': repo.get('watchers_count'),
                'forks_count': repo.get('forks_count'),
                'size': repo.get('size'),
                'default_branch': repo.get('default_branch'),
                'created_at': repo.get('created_at'),
                'updated_at': repo.get('updated_at'),
                'pushed_at': repo.get('pushed_at'),
                'archived': repo.get('archived'),
                'disabled': repo.get('disabled'),
                'fork': repo.get('fork'),
                'topics': repo.get('topics', []),
                'visibility': repo.get('visibility')
            }
            repositories.append(repo_info)
        
        return jsonify({
            'repositories': repositories,
            'page': page,
            'per_page': per_page,
            'total_count': len(repositories)
        })
    else:
        return jsonify({'error': f'Failed to fetch repositories from GitHub'}), repos_response.status_code

# Health check endpoint
@app.route('/api/health')
def health():
    return jsonify({'status': 'ok'})

# Debug endpoint to check configuration
@app.route('/api/config')
def config():
    return jsonify({
        'callback_url': CALLBACK_URL,
        'frontend_url': FRONTEND_URL,
        'backend_port': BACKEND_PORT,
        'github_client_id': GITHUB_CLIENT_ID[:8] + '...' if GITHUB_CLIENT_ID != 'your_client_id' else 'NOT_SET'
    })

if __name__ == '__main__':
    app.run(debug=True, port=BACKEND_PORT)
