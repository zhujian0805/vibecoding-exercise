from flask import Flask, redirect, url_for, session, request, jsonify
from flask_cors import CORS
from flask_caching import Cache
import os
import requests
import time
import logging
import hashlib
import json
from github import Github
from github.GithubException import GithubException
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial, wraps

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_secret_key')

# Configure caching
cache_config = {
    'CACHE_TYPE': os.environ.get('CACHE_TYPE', 'simple'),  # fallback to simple cache
    'CACHE_DEFAULT_TIMEOUT': int(os.environ.get('CACHE_DEFAULT_TIMEOUT', '300')),  # 5 minutes default
}

# Redis configuration if available
if os.environ.get('REDIS_URL'):
    cache_config.update({
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_URL': os.environ.get('REDIS_URL'),
    })
elif os.environ.get('REDIS_HOST'):
    cache_config.update({
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_HOST': os.environ.get('REDIS_HOST', 'localhost'),
        'CACHE_REDIS_PORT': int(os.environ.get('REDIS_PORT', '6379')),
        'CACHE_REDIS_DB': int(os.environ.get('REDIS_DB', '0')),
        'CACHE_REDIS_PASSWORD': os.environ.get('REDIS_PASSWORD'),
    })

cache = Cache(app, config=cache_config)

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

# Cache configuration constants
CACHE_TIMEOUT_SHORT = 60  # 1 minute for rate limits
CACHE_TIMEOUT_MEDIUM = 300  # 5 minutes for user profile
CACHE_TIMEOUT_LONG = 600   # 10 minutes for repositories
CACHE_TIMEOUT_VERY_LONG = 1800  # 30 minutes for static data

def generate_cache_key(prefix, user_id, *args):
    """Generate a consistent cache key for user-specific data"""
    key_parts = [str(prefix), str(user_id)] + [str(arg) for arg in args]
    key_string = ':'.join(key_parts)
    # Hash long keys to avoid Redis key length limits
    if len(key_string) > 100:
        key_string = f"{prefix}:{user_id}:{hashlib.md5(key_string.encode()).hexdigest()}"
    return key_string

def cache_user_data(prefix, timeout=CACHE_TIMEOUT_MEDIUM):
    """Decorator to cache user-specific data"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get user ID from session
            user = session.get('user')
            if not user:
                return func(*args, **kwargs)
            
            user_id = user.get('id')
            if not user_id:
                return func(*args, **kwargs)
            
            # Generate cache key with function arguments
            cache_key = generate_cache_key(prefix, user_id, str(args), str(sorted(kwargs.items())))
            
            # Try to get from cache
            try:
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for key: {cache_key}")
                    return cached_result
            except Exception as e:
                logger.warning(f"Cache get failed for {cache_key}: {e}")
            
            # Execute function and cache result
            try:
                result = func(*args, **kwargs)
                cache.set(cache_key, result, timeout=timeout)
                logger.debug(f"Cache set for key: {cache_key} (timeout: {timeout}s)")
                return result
            except Exception as e:
                logger.error(f"Function execution failed for {cache_key}: {e}")
                raise
        return wrapper
    return decorator

def invalidate_user_cache(user_id, prefix=None):
    """Invalidate cache for a specific user"""
    try:
        if prefix:
            # If using Redis, we could use pattern matching
            cache_key = generate_cache_key(prefix, user_id, '*')
            # For simple cache, we'll need to track keys manually
            pass
        else:
            # Clear all cache if no prefix specified
            cache.clear()
        logger.debug(f"Cache invalidated for user {user_id}, prefix: {prefix}")
    except Exception as e:
        logger.warning(f"Cache invalidation failed: {e}")

def check_rate_limit(g):
    """Check GitHub API rate limit and log the status"""
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
    # Get user ID before clearing session
    user = session.get('user')
    if user and user.get('id'):
        user_id = user.get('id')
        # Clear user-specific cache
        invalidate_user_cache(user_id)
    
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/api/profile')
@cache_user_data('profile', CACHE_TIMEOUT_MEDIUM)
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

def process_single_repo(repo):
    """Process a single repository object and extract its information"""
    try:
        # Get topics safely
        topics = []
        try:
            if hasattr(repo, 'get_topics'):
                topics = list(repo.get_topics())
        except Exception:
            topics = []
        
        return {
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
    except Exception as e:
        print(f"[DEBUG] Error processing repo {getattr(repo, 'name', 'unknown')}: {e}")
        return None

def get_cached_repositories(access_token, user_id, sort='updated', limit=None, visibility='all'):
    """Get repositories with caching support"""
    # Use a reasonable default limit to avoid memory issues, but allow unlimited
    effective_limit = limit if limit is not None else 1000  # Default to 1000 for caching key
    cache_key = generate_cache_key('repos', user_id, sort, effective_limit, visibility)
    
    try:
        cached_repos = cache.get(cache_key)
        if cached_repos is not None:
            logger.debug(f"Repository cache hit for user {user_id}")
            # If no limit specified, return all cached repos
            if limit is None:
                return cached_repos
            # Otherwise return limited results
            return cached_repos[:limit]
    except Exception as e:
        logger.warning(f"Repository cache get failed: {e}")
    
    # Fetch repositories from GitHub API
    try:
        g = Github(access_token)
        user = g.get_user()
        
        # Collect repository objects
        repo_objects = []
        repo_count = 0
        
        for repo in user.get_repos(visibility=visibility, sort=sort):
            repo_count += 1
            repo_objects.append(repo)
            
            # Only stop if we have a specific limit and reached it
            if limit is not None and len(repo_objects) >= limit:
                break
            
            # Safety limit to prevent memory issues (can be configured)
            max_repos = int(os.environ.get('MAX_REPOS_FETCH', '2000'))
            if len(repo_objects) >= max_repos:
                logger.warning(f"Reached maximum repository fetch limit of {max_repos}")
                break
        
        # Process repositories in parallel
        all_repositories = []
        max_workers = min(10, len(repo_objects))
        
        if repo_objects:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_repo = {
                    executor.submit(process_single_repo, repo): repo 
                    for repo in repo_objects
                }
                
                for future in as_completed(future_to_repo):
                    repo = future_to_repo[future]
                    try:
                        result = future.result(timeout=30)
                        if result:
                            all_repositories.append(result)
                    except Exception as e:
                        logger.error(f"Failed to process repo {getattr(repo, 'name', 'unknown')}: {e}")
        
        # Sort results
        if sort == 'updated':
            all_repositories.sort(key=lambda x: x['updated_at'] or '', reverse=True)
        elif sort == 'created':
            all_repositories.sort(key=lambda x: x['created_at'] or '', reverse=True)
        elif sort == 'pushed':
            all_repositories.sort(key=lambda x: x['pushed_at'] or '', reverse=True)
        elif sort == 'full_name':
            all_repositories.sort(key=lambda x: x['full_name'].lower())
        
        # Cache the results (cache all fetched repos)
        try:
            cache.set(cache_key, all_repositories, timeout=CACHE_TIMEOUT_LONG)
            logger.debug(f"Cached {len(all_repositories)} repositories for user {user_id}")
        except Exception as e:
            logger.warning(f"Repository cache set failed: {e}")
        
        return all_repositories
        
    except Exception as e:
        logger.error(f"Failed to fetch repositories: {e}")
        raise

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
    
    user = session.get('user', {})
    user_id = user.get('id')
    user_login = user.get('login', 'unknown')
    print(f"[DEBUG] User: {user_login}")
    
    try:
        # Get parameters
        sort = request.args.get('sort', 'updated')
        # Remove the hardcoded limit - let it fetch all repositories
        limit_param = request.args.get('limit')
        limit = int(limit_param) if limit_param else None  # No limit by default
        visibility = request.args.get('visibility', 'all')  # all, public, private
        search_query = request.args.get('search', '').strip().lower()  # Search parameter
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 30)), 100)  # Per page parameter
        
        print(f"[DEBUG] Parameters - sort: {sort}, limit: {limit}, visibility: {visibility}, search: '{search_query}', page: {page}, per_page: {per_page}")
        
        # Check rate limit first (with short cache)
        rate_limit_cache_key = generate_cache_key('rate_limit', user_id)
        rate_limit_ok = cache.get(rate_limit_cache_key)
        
        if rate_limit_ok is None:
            print("[DEBUG] Checking rate limit...")
            g = Github(access_token)
            rate_limit_ok = check_rate_limit(g)
            cache.set(rate_limit_cache_key, rate_limit_ok, timeout=CACHE_TIMEOUT_SHORT)
        else:
            print("[DEBUG] Rate limit check cached")
        
        if not rate_limit_ok:
            return jsonify({'error': 'Rate limit too low, please try again later'}), 429
        
        print(f"[DEBUG] Fetching repositories using cached method...")
        fetch_start = time.time()
        
        # Get cached repositories
        all_repositories = get_cached_repositories(access_token, user_id, sort, limit, visibility)
        
        # Apply search filter if needed
        if search_query:
            filtered_repos = []
            for repo in all_repositories:
                repo_name = repo['name'].lower()
                repo_full_name = repo['full_name'].lower()
                repo_description = (repo['description'] or '').lower()
                
                if (search_query in repo_name or 
                    search_query in repo_full_name or 
                    search_query in repo_description):
                    filtered_repos.append(repo)
            
            all_repositories = filtered_repos
        
        # Calculate pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_repos = all_repositories[start_idx:end_idx]
        
        print(f"[DEBUG] Returning repositories {start_idx+1} to {min(end_idx, len(all_repositories))} of {len(all_repositories)}")
        
        fetch_time = time.time() - fetch_start
        total_time = time.time() - start_time
        print(f"[DEBUG] Processed {len(paginated_repos)} repositories in {fetch_time:.2f}s")
        print(f"[DEBUG] Total processing time: {total_time:.2f}s")
        
        result = {
            'repositories': paginated_repos,
            'page': page,
            'per_page': per_page,
            'total_count': len(all_repositories),
            'total_pages': (len(all_repositories) + per_page - 1) // per_page if len(all_repositories) > 0 else 1,
            'has_next': end_idx < len(all_repositories),
            'has_prev': page > 1,
            'search_query': search_query,
            'debug_info': {
                'processing_time': total_time,
                'fetch_time': fetch_time,
                'repos_total': len(all_repositories),
                'repos_returned': len(paginated_repos),
                'cache_enabled': True
            }
        }
        
        print(f"[DEBUG] Returning {len(paginated_repos)} repositories (page {page}/{result['total_pages']})")
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

# Cache management endpoints
@app.route('/api/cache/status')
def cache_status():
    """Get cache configuration and status"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        cache_type = cache.config.get('CACHE_TYPE', 'unknown')
        return jsonify({
            'cache_type': cache_type,
            'cache_timeout_short': CACHE_TIMEOUT_SHORT,
            'cache_timeout_medium': CACHE_TIMEOUT_MEDIUM,
            'cache_timeout_long': CACHE_TIMEOUT_LONG,
            'cache_timeout_very_long': CACHE_TIMEOUT_VERY_LONG,
            'redis_configured': cache_type == 'redis'
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get cache status: {str(e)}'}), 500

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear user-specific cache"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = session.get('user')
    user_id = user.get('id') if user else None
    
    if not user_id:
        return jsonify({'error': 'User ID not found'}), 400
    
    try:
        # Clear user-specific cache
        invalidate_user_cache(user_id)
        return jsonify({'message': 'Cache cleared successfully'})
    except Exception as e:
        return jsonify({'error': f'Failed to clear cache: {str(e)}'}), 500

@app.route('/api/cache/clear-all', methods=['POST'])
def clear_all_cache():
    """Clear all cache (admin function)"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        cache.clear()
        return jsonify({'message': 'All cache cleared successfully'})
    except Exception as e:
        return jsonify({'error': f'Failed to clear all cache: {str(e)}'}), 500

# Debug endpoint to check configuration
@app.route('/api/config')
def config():
    cache_type = 'unknown'
    try:
        cache_type = cache.config.get('CACHE_TYPE', 'unknown')
    except:
        pass
    
    return jsonify({
        'callback_url': CALLBACK_URL,
        'frontend_url': FRONTEND_URL,
        'backend_port': BACKEND_PORT,
        'github_client_id': GITHUB_CLIENT_ID[:8] + '...' if GITHUB_CLIENT_ID != 'your_client_id' else 'NOT_SET',
        'cache_type': cache_type
    })

# Debug endpoint to check rate limits
@app.route('/api/debug/rate-limit')
def debug_rate_limit():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({'error': 'No access token'}), 401
    
    user = session.get('user', {})
    user_id = user.get('id')
    
    # Check if we have cached rate limit info
    rate_limit_cache_key = generate_cache_key('rate_limit_full', user_id)
    cached_rate_limit = cache.get(rate_limit_cache_key)
    
    if cached_rate_limit:
        cached_rate_limit['cached'] = True
        return jsonify(cached_rate_limit)
    
    try:
        g = Github(access_token)
        rate_limit = g.get_rate_limit()
        
        result = {
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
            },
            'cached': False
        }
        
        # Cache for a short time
        cache.set(rate_limit_cache_key, result, timeout=CACHE_TIMEOUT_SHORT)
        
        return jsonify(result)
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
    print(f"[DEBUG] Cache type: {cache.config.get('CACHE_TYPE', 'unknown')}")
    print(f"[DEBUG] Cache timeouts - Short: {CACHE_TIMEOUT_SHORT}s, Medium: {CACHE_TIMEOUT_MEDIUM}s, Long: {CACHE_TIMEOUT_LONG}s")
    print(f"[DEBUG] Available endpoints:")
    print(f"[DEBUG]   - /api/cache/status (cache configuration)")
    print(f"[DEBUG]   - /api/cache/clear (clear user cache)")
    print(f"[DEBUG]   - /api/cache/clear-all (clear all cache)")
    print(f"[DEBUG] Available debug endpoints:")
    print(f"[DEBUG]   - /api/debug/rate-limit")
    print(f"[DEBUG]   - /api/debug/simple-repos")
    print(f"[DEBUG]   - /api/config")
    print(f"[DEBUG]   - /api/health")
    app.run(debug=True, port=BACKEND_PORT)
