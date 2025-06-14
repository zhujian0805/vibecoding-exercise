from flask import Flask, redirect, url_for, session, request, jsonify
from flask_cors import CORS
import os
import requests
from github import Github
from github.GithubException import GithubException

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
    # Include repo scope to access all repositories (public and private)
    # read:user for user profile, repo for repository access
    scope = "read:user repo"
    return jsonify({
        'auth_url': f"{GITHUB_AUTH_URL}?client_id={GITHUB_CLIENT_ID}&scope={scope}&redirect_uri={callback_url}"
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
    
    try:
        # Get user info using PyGithub
        g = Github(access_token)
        user = g.get_user()
        
        # Convert user info to dict for session storage
        user_json = {
            'login': user.login,
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'avatar_url': user.avatar_url
        }
        
        session['user'] = user_json
        session['access_token'] = access_token
        
        # Redirect to React app after successful authentication
        return redirect(f"{FRONTEND_URL}/")
        
    except GithubException as e:
        return redirect(f"{FRONTEND_URL}/login?error=github_api_failed")
    except Exception as e:
        return redirect(f"{FRONTEND_URL}/login?error=user_fetch_failed")

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
    
    try:
        # Initialize GitHub client with access token
        g = Github(access_token)
        
        # Get authenticated user information
        user = g.get_user()
        
        # Extract relevant user information
        user_info = {
            'login': user.login,
            'name': user.name,
            'email': user.email,
            'avatar_url': user.avatar_url,
            'bio': user.bio,
            'location': user.location,
            'company': user.company,
            'blog': user.blog,
            'twitter_username': user.twitter_username,
            'public_repos': user.public_repos,
            'followers': user.followers,
            'following': user.following,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None,
            'html_url': user.html_url
        }
        
        return jsonify(user_info)
        
    except GithubException as e:
        return jsonify({'error': f'GitHub API error: {e.data.get("message", str(e))}'}), e.status
    except Exception as e:
        return jsonify({'error': f'Failed to fetch user information: {str(e)}'}), 500

@app.route('/api/repositories')
def repositories():
    # Check if user is logged in
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get access token from session
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({'error': 'No access token'}), 401
    
    try:
        # Initialize GitHub client with access token
        g = Github(access_token)
        
        # Get authenticated user
        user = g.get_user()
        
        # Get sort parameter
        sort = request.args.get('sort', 'updated')
        
        all_repositories = []
        seen_repo_ids = set()  # Track seen repositories to avoid duplicates
        
        # Get all repositories with different affiliation types
        affiliations = ['owner', 'collaborator', 'organization_member']
        
        for affiliation in affiliations:
            try:
                # Get repositories for this affiliation type
                repos = user.get_repos(
                    visibility='all',
                    affiliation=affiliation,
                    sort=sort
                )
                
                # Process all repositories for this affiliation
                for repo in repos:
                    # Check if we already have this repository (to avoid duplicates)
                    if repo.id not in seen_repo_ids:
                        seen_repo_ids.add(repo.id)
                        
                        repo_info = {
                            'id': repo.id,
                            'name': repo.name,
                            'full_name': repo.full_name,
                            'description': repo.description,
                            'private': repo.private,
                            'html_url': repo.html_url,
                            'clone_url': repo.clone_url,
                            'ssh_url': repo.ssh_url,
                            'language': repo.language,
                            'stargazers_count': repo.stargazers_count,
                            'watchers_count': repo.watchers_count,
                            'forks_count': repo.forks_count,
                            'size': repo.size,
                            'default_branch': repo.default_branch,
                            'created_at': repo.created_at.isoformat() if repo.created_at else None,
                            'updated_at': repo.updated_at.isoformat() if repo.updated_at else None,
                            'pushed_at': repo.pushed_at.isoformat() if repo.pushed_at else None,
                            'archived': repo.archived,
                            'disabled': repo.disabled,
                            'fork': repo.fork,
                            'topics': list(repo.get_topics()) if hasattr(repo, 'get_topics') else [],
                            'visibility': repo.visibility if hasattr(repo, 'visibility') else ('private' if repo.private else 'public'),
                            'affiliation': affiliation,
                            'owner': {
                                'login': repo.owner.login,
                                'type': repo.owner.type
                            }
                        }
                        all_repositories.append(repo_info)
                        
            except GithubException as e:
                # Log the error but continue with other affiliations
                print(f"Warning: Failed to fetch {affiliation} repositories: {e.data.get('message', str(e))}")
                continue
        
        return jsonify({
            'repositories': all_repositories,
            'total_count': len(all_repositories),
            'fetched_all': True
        })
        
    except GithubException as e:
        return jsonify({'error': f'GitHub API error: {e.data.get("message", str(e))}'}), e.status
    except Exception as e:
        return jsonify({'error': f'Failed to fetch repositories: {str(e)}'}), 500

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
