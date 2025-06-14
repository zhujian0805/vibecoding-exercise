from flask import Flask, redirect, url_for, session, request, jsonify
from flask_cors import CORS
import os
import requests
import time
import logging
from github import Github
from github.GithubException import GithubException

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

def check_rate_limit(g):
    """Check GitHub API rate limit and log the status"""
    try:
        rate_limit = g.get_rate_limit()
        core_limit = rate_limit.core
        print(f"[DEBUG] Rate limit status - Remaining: {core_limit.remaining}/{core_limit.limit}, Resets at: {core_limit.reset}")
        
        if core_limit.remaining < 10:
            print(f"[WARNING] Low rate limit remaining: {core_limit.remaining}")
            return False
        return True
    except Exception as e:
        print(f"[DEBUG] Failed to check rate limit: {e}")
        return True

def with_timeout(func, timeout_seconds=30):
    """Simple timeout wrapper for API calls"""
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {timeout_seconds} seconds")
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    
    try:
        result = func()
        signal.alarm(0)  # Cancel the alarm
        return result
    except TimeoutError:
        print(f"[DEBUG] Operation timed out after {timeout_seconds} seconds")
        raise
    finally:
        signal.alarm(0)  # Ensure alarm is cancelled

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
    start_time = time.time()
    print(f"[DEBUG] /api/repositories called at {request.remote_addr} - Start time: {start_time}")
    
    # Check if user is logged in
    if 'user' not in session:
        print("[DEBUG] User not authenticated")
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get access token from session
    access_token = session.get('access_token')
    if not access_token:
        print("[DEBUG] No access token found")
        return jsonify({'error': 'No access token'}), 401
    
    print(f"[DEBUG] User: {session.get('user', {}).get('login', 'unknown')}")
    
    try:
        print("[DEBUG] Initializing GitHub client...")
        # Initialize GitHub client with access token (similar to your example)
        g = Github(access_token)
        
        # Check rate limit first
        if not check_rate_limit(g):
            return jsonify({'error': 'Rate limit too low, please try again later'}), 429
        
        print("[DEBUG] Getting authenticated user...")
        # Get authenticated user
        user = g.get_user()
        print(f"[DEBUG] User retrieved: {user.login}")
        
        # Get parameters
        sort = request.args.get('sort', 'updated')
        limit = min(int(request.args.get('limit', 50)), 200)  # Limit to prevent timeouts
        visibility = request.args.get('visibility', 'all')  # all, public, private
        print(f"[DEBUG] Parameters - sort: {sort}, limit: {limit}, visibility: {visibility}")
        
        all_repositories = []
        repo_count = 0
        
        print(f"[DEBUG] Fetching repositories using auto-paginated approach...")
        fetch_start = time.time()
        
        # Use the simpler approach from your example - auto-paginated
        for repo in user.get_repos(visibility=visibility, sort=sort):
            repo_start = time.time()
            repo_count += 1
            
            print(f"[DEBUG] Processing repo {repo_count}: {repo.full_name}")
            
            # Get topics safely (this was causing slowdowns before)
            topics = []
            try:
                if hasattr(repo, 'get_topics'):
                    topics = list(repo.get_topics())
                    print(f"[DEBUG] Got {len(topics)} topics for {repo.full_name}")
            except Exception as topic_error:
                print(f"[DEBUG] Failed to get topics for {repo.full_name}: {topic_error}")
                topics = []
            
            # Build repo info
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
                'topics': topics,
                'visibility': repo.visibility if hasattr(repo, 'visibility') else ('private' if repo.private else 'public'),
                'owner': {
                    'login': repo.owner.login,
                    'type': repo.owner.type
                }
            }
            
            all_repositories.append(repo_info)
            repo_time = time.time() - repo_start
            print(f"[DEBUG] Added repo {repo.full_name} (total: {len(all_repositories)}) in {repo_time:.2f}s")
            
            # Stop if we've reached our limit
            if len(all_repositories) >= limit:
                print(f"[DEBUG] Reached limit of {limit} repositories")
                break
        
        fetch_time = time.time() - fetch_start
        total_time = time.time() - start_time
        print(f"[DEBUG] Fetched {len(all_repositories)} repositories in {fetch_time:.2f}s")
        print(f"[DEBUG] Total processing time: {total_time:.2f}s")
        
        result = {
            'repositories': all_repositories,
            'total_count': len(all_repositories),
            'limited_to': limit,
            'fetched_all': len(all_repositories) < limit,
            'debug_info': {
                'processing_time': total_time,
                'fetch_time': fetch_time,
                'repos_processed': repo_count
            }
        }
        
        print(f"[DEBUG] Returning {len(all_repositories)} repositories")
        return jsonify(result)
        
    except GithubException as e:
        error_msg = f'GitHub API error: {e.data.get("message", str(e)) if hasattr(e, "data") and e.data else str(e)}'
        print(f"[DEBUG] GithubException in repositories endpoint: {error_msg}")
        return jsonify({'error': error_msg}), getattr(e, 'status', 500)
    except Exception as e:
        error_msg = f'Failed to fetch repositories: {str(e)}'
        print(f"[DEBUG] Exception in repositories endpoint: {error_msg}")
        return jsonify({'error': error_msg}), 500

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

# Debug endpoint to check rate limits
@app.route('/api/debug/rate-limit')
def debug_rate_limit():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({'error': 'No access token'}), 401
    
    try:
        g = Github(access_token)
        rate_limit = g.get_rate_limit()
        
        return jsonify({
            'core': {
                'limit': rate_limit.core.limit,
                'remaining': rate_limit.core.remaining,
                'reset': rate_limit.core.reset.isoformat(),
                'used': rate_limit.core.used
            },
            'search': {
                'limit': rate_limit.search.limit,
                'remaining': rate_limit.search.remaining,
                'reset': rate_limit.search.reset.isoformat(),
                'used': rate_limit.search.used
            }
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get rate limit: {str(e)}'}), 500

# Debug endpoint to test simple repo fetch
@app.route('/api/debug/simple-repos')
def debug_simple_repos():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({'error': 'No access token'}), 401
    
    try:
        start_time = time.time()
        # Initialize like your example
        g = Github(access_token)
        user = g.get_user()
        
        # Use the simple auto-paginated approach, but limit to 5 repos
        simple_repos = []
        for repo in user.get_repos(visibility='all'):
            simple_repos.append({
                'name': repo.name,
                'full_name': repo.full_name,
                'private': repo.private,
                'clone_url': repo.clone_url  # Following your example pattern
            })
            if len(simple_repos) >= 5:
                break
        
        end_time = time.time()
        return jsonify({
            'repositories': simple_repos,
            'count': len(simple_repos),
            'processing_time': end_time - start_time
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch simple repos: {str(e)}'}), 500

if __name__ == '__main__':
    print(f"[DEBUG] Starting Flask app...")
    print(f"[DEBUG] Backend port: {BACKEND_PORT}")
    print(f"[DEBUG] Backend host: {BACKEND_HOST}")
    print(f"[DEBUG] Frontend URL: {FRONTEND_URL}")
    print(f"[DEBUG] Callback URL: {CALLBACK_URL}")
    print(f"[DEBUG] GitHub Client ID: {GITHUB_CLIENT_ID[:8]}..." if GITHUB_CLIENT_ID != 'your_client_id' else "[DEBUG] GitHub Client ID: NOT_SET")
    print(f"[DEBUG] Available debug endpoints:")
    print(f"[DEBUG]   - /api/debug/rate-limit")
    print(f"[DEBUG]   - /api/debug/simple-repos")
    print(f"[DEBUG]   - /api/config")
    print(f"[DEBUG]   - /api/health")
    app.run(debug=True, port=BACKEND_PORT)
