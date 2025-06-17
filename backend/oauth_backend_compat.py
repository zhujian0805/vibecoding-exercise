"""
Backward compatibility entry point for the refactored OAuth backend.
This file redirects to the new modular architecture in main.py.

The original monolithic code has been refactored into:
- main.py - Application entry point
- app_factory.py - Application factory with dependency injection
- controllers/ - Route controllers (auth_controller.py, repository_controller.py)
- services/ - Business logic services (auth_service.py, repository_service.py, cache_service.py)
- models/ - Data models (user.py, repository.py)
- config.py - Configuration management
"""

import logging
import sys

logger = logging.getLogger(__name__)


def main():
    """Main entry point that delegates to the refactored application"""
    try:
        # Import and run the new refactored app
        from main import main as refactored_main
        logger.info("Starting refactored OAuth backend application...")
        refactored_main()
        
    except ImportError as e:
        logger.error(f"Could not import refactored modules: {e}")
        logger.error("Please ensure all required modules are installed and available.")
        logger.error("Required modules: app_factory, controllers, services, models, config")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
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

# Configure session settings for proper cookie handling
app.config.update(
    SESSION_COOKIE_HTTPONLY=False,   # Allow JavaScript access
    SESSION_COOKIE_SAMESITE='Lax',   # Allow cross-site requests for OAuth
    SESSION_COOKIE_SECURE=False,     # Set to True in production with HTTPS
    SESSION_COOKIE_DOMAIN='localhost',  # Share cookies across localhost
    SESSION_COOKIE_PATH='/',         # Make cookies available to all paths
    PERMANENT_SESSION_LIFETIME=3600  # 1 hour
)

# Configure caching
cache_config = {
    'CACHE_TYPE': os.environ.get('CACHE_TYPE', 'simple'),  # fallback to simple cache
    'CACHE_DEFAULT_TIMEOUT': int(os.environ.get('CACHE_DEFAULT_TIMEOUT', '3600')),  # 1 hour default
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

cache = Cache(app, config=cache_config)    # Add cache manager instantiation
try:
    from services.cache_service import CacheManager
except ImportError:
    from cache_manager import CacheManager
cache_manager = CacheManager(cache)

# Enable CORS for React frontend on port 80
CORS(app, 
     supports_credentials=True, 
     origins=['http://localhost', 'http://localhost:80', 'http://localhost:3000', 'http://127.0.0.1', 'http://127.0.0.1:80'],
     allow_headers=['Content-Type', 'Authorization', 'Cookie'],
     expose_headers=['Set-Cookie'],
     methods=['GET', 'POST', 'OPTIONS'])

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
CACHE_TIMEOUT_MEDIUM = 3600  # 1 hour for user profile
CACHE_TIMEOUT_LONG = 3600   # 1 hour for repositories

@app.route('/api/user')
def get_user():
    # Debug session information
    logger.debug(f"[DEBUG] get_user() called")
    logger.debug(f"[DEBUG] Session keys: {list(session.keys())}")
    logger.debug(f"[DEBUG] Session ID: {session.get('_id', 'NO_ID')}")
    logger.debug(f"[DEBUG] Request headers: {dict(request.headers)}")
    logger.debug(f"[DEBUG] Request cookies: {request.cookies}")
    
    user = session.get('user')
    if user:
        response_data = {'authenticated': True, 'user': user}
        logger.debug(f"[DEBUG] get_user() returning data: {json.dumps(response_data, indent=2, default=str)}")
        print(f"[DEBUG] get_user() return object: {json.dumps(response_data, indent=2, default=str)}")
        return jsonify(response_data)
    
    response_data = {'authenticated': False}
    logger.debug(f"[DEBUG] get_user() returning data (unauthenticated): {json.dumps(response_data, indent=2, default=str)}")
    print(f"[DEBUG] get_user() return object (unauthenticated): {json.dumps(response_data, indent=2, default=str)}")
    return jsonify(response_data), 401

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
    logger.debug(f"[DEBUG] Callback called with args: {request.args}")
    logger.debug(f"[DEBUG] Session before callback: {dict(session)}")
    
    code = request.args.get('code')
    if not code:
        logger.error("[ERROR] No authorization code received")
        return redirect(f"{FRONTEND_URL}/login?error=no_code")
    
    logger.debug(f"[DEBUG] Received authorization code: {code[:10]}...")
    
    # Exchange code for access token
    try:
        token_resp = requests.post(
            GITHUB_TOKEN_URL,
            headers={'Accept': 'application/json'},
            data={
                'client_id': GITHUB_CLIENT_ID,
                'client_secret': GITHUB_CLIENT_SECRET,
                'code': code
            },
            timeout=10
        )
        
        logger.debug(f"[DEBUG] Token response status: {token_resp.status_code}")
        
        if token_resp.status_code != 200:
            logger.error(f"[ERROR] Token request failed with status {token_resp.status_code}: {token_resp.text}")
            return redirect(f"{FRONTEND_URL}/login?error=token_failed")
            
        token_json = token_resp.json()
        logger.debug(f"[DEBUG] Token response: {list(token_json.keys())}")
        
        access_token = token_json.get('access_token')
        if not access_token:
            logger.error(f"[ERROR] No access token in response: {token_json}")
            return redirect(f"{FRONTEND_URL}/login?error=token_failed")
            
        logger.debug(f"[DEBUG] Access token received: {access_token[:10]}...")
        
    except requests.RequestException as e:
        logger.error(f"[ERROR] Token request exception: {str(e)}")
        return redirect(f"{FRONTEND_URL}/login?error=token_request_failed")
    except Exception as e:
        logger.error(f"[ERROR] Unexpected error during token exchange: {str(e)}")
        return redirect(f"{FRONTEND_URL}/login?error=token_exchange_failed")

    try:
        # Get user info using PyGithub
        logger.debug("[DEBUG] Creating GitHub client...")
        g = Github(access_token)
        user = g.get_user()
        
        logger.debug(f"[DEBUG] GitHub user fetched: {user.login}")
        
        # Get total repository count (public + private) using totalCount
        try:
            repo_list = user.get_repos()
            total_repos = repo_list.totalCount
            logger.debug(f"[DEBUG] Found {total_repos} total repositories for user {user.login} using totalCount")
        except Exception as e:
            logger.warning(f"[WARNING] Failed to fetch total repo count for {user.login}: {e}")
            total_repos = user.public_repos  # fallback to public repos count
        
        # Convert full user info to dict for session storage
        user_json = {
            'login': user.login,
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'avatar_url': user.avatar_url,
            'bio': user.bio,
            'location': user.location,
            'company': user.company,
            'blog': user.blog,
            'twitter_username': getattr(user, 'twitter_username', None),
            'public_repos': user.public_repos,
            'total_repos': total_repos,
            'followers': user.followers,
            'following': user.following,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None,
            'html_url': user.html_url
        }
        
        # Ensure total_repos is included - debug logging
        logger.debug(f"[DEBUG] Creating user_json with total_repos: {total_repos}")
        logger.debug(f"[DEBUG] user_json after creation: {json.dumps(user_json, indent=2, default=str)}")
        
        logger.debug(f"OAuth callback - storing user data for {user.login}")
        logger.debug(f"  public_repos: {user_json['public_repos']}")
        logger.debug(f"  total_repos: {user_json['total_repos']}")
        logger.debug(f"  followers: {user_json['followers']}")
        logger.debug(f"  following: {user_json['following']}")
        
        # Store user data and access token in session
        session['user'] = user_json
        session['access_token'] = access_token
        session.permanent = True  # Make session persistent
        
        # Debug: verify session was set
        logger.debug(f"[DEBUG] Session after setting user: user={session.get('user', {}).get('login', 'NOT_SET')}")
        logger.debug(f"[DEBUG] Session ID: {session.get('_id', 'NO_ID')}")
        logger.debug(f"[DEBUG] Full session after callback: {dict(session)}")
        print(f"[DEBUG] OAuth callback completed for user: {user.login}")
        print(f"[DEBUG] Session user set to: {session.get('user', {}).get('login', 'NOT_SET')}")
        
        # Redirect to React app after successful authentication
        return redirect(f"{FRONTEND_URL}/")
        
    except GithubException as e:
        logger.error(f"[ERROR] GitHub API exception: {str(e)}")
        return redirect(f"{FRONTEND_URL}/login?error=github_api_failed")
    except Exception as e:
        logger.error(f"[ERROR] Unexpected error during user fetch: {str(e)}")
        logger.exception("Full traceback:")
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
@cache_manager.cache_user_data('profile', CACHE_TIMEOUT_MEDIUM)
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
        
        # Get total repository count (public + private) using totalCount
        try:
            repo_list = user.get_repos()
            total_repos = repo_list.totalCount
            logger.debug(f"[DEBUG] Found {total_repos} total repositories for user {user.login} using totalCount")
        except Exception as e:
            logger.warning(f"[WARNING] Failed to fetch total repo count for {user.login}: {e}")
            total_repos = user.public_repos  # fallback to public repos count
        
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
            'total_repos': total_repos,
            'followers': user.followers,
            'following': user.following,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None,
            'html_url': user.html_url
        }
        
        # Debug logging
        logger.debug(f"Profile data for user {user.login}:")
        logger.debug(f"  public_repos: {user_info['public_repos']} (type: {type(user_info['public_repos'])})")
        logger.debug(f"  total_repos: {user_info['total_repos']} (type: {type(user_info['total_repos'])})")
        logger.debug(f"  followers: {user_info['followers']} (type: {type(user_info['followers'])})")
        logger.debug(f"  following: {user_info['following']} (type: {type(user_info['following'])})")
        
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

def fetch_repos_page(access_token, page, per_page=100):
    """Fetch a single page of repositories using direct API call"""
    url = f"https://api.github.com/user/repos"
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    params = {
        'visibility': 'all',
        'sort': 'updated',
        'page': page,
        'per_page': per_page
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch page {page}: {e}")
        return []

def get_total_repo_count(access_token):
    """Get the total number of repositories to determine how many pages to fetch"""
    try:
        g = Github(access_token)
        user = g.get_user()
        return user.public_repos + user.total_private_repos
    except Exception as e:
        logger.warning(f"Failed to get repo count, using fallback method: {e}")
        # Fallback: fetch first page to get total from headers
        try:
            url = "https://api.github.com/user/repos"
            headers = {
                'Authorization': f'token {access_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            params = {'visibility': 'all', 'sort': 'updated', 'page': 1, 'per_page': 1}
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            # Try to get total from Link header pagination info
            link_header = response.headers.get('Link', '')
            if 'rel="last"' in link_header:
                # Extract last page number from Link header
                import re
                last_page_match = re.search(r'page=(\d+)[^>]*>\s*;\s*rel="last"', link_header)
                if last_page_match:
                    last_page = int(last_page_match.group(1))
                    return last_page * 100  # Rough estimate
            
            # If no pagination info, assume less than 100 repos
            return len(response.json()) if response.json() else 0
        except Exception:
            return 100  # Conservative fallback

def get_all_user_repositories(access_token, user_id):
    """Get all repositories for a user with parallelized page fetching"""
    cache_key = generate_cache_key('repos', user_id)
    
    try:
        cached_repos = cache.get(cache_key)
        if cached_repos is not None:
            logger.debug(f"Repository cache hit for user {user_id}")
            return cached_repos
    except Exception as e:
        logger.warning(f"Repository cache get failed: {e}")
    
    # Fetch repositories from GitHub API with parallel pagination
    try:
        # First, determine how many pages we need to fetch
        total_repos = get_total_repo_count(access_token)
        max_repos = int(os.environ.get('MAX_REPOS_FETCH', '2000'))
        actual_limit = min(total_repos, max_repos)
        
        per_page = 100  # GitHub's maximum per page
        num_pages = (actual_limit + per_page - 1) // per_page  # Ceiling division
        
        logger.debug(f"Fetching {actual_limit} repositories across {num_pages} pages in parallel")
        
        # Fetch all pages in parallel
        all_repo_data = []
        max_workers = min(10, num_pages)  # Limit concurrent API calls to be respectful
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all page fetch tasks
            future_to_page = {
                executor.submit(fetch_repos_page, access_token, page + 1, per_page): page + 1
                for page in range(num_pages)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_page):
                page_num = future_to_page[future]
                try:
                    page_data = future.result(timeout=30)
                    if page_data:
                        all_repo_data.extend(page_data)
                        logger.debug(f"Successfully fetched page {page_num} with {len(page_data)} repos")
                    else:
                        logger.warning(f"Page {page_num} returned no data")
                except Exception as e:
                    logger.error(f"Failed to fetch page {page_num}: {e}")
        
        logger.debug(f"Fetched {len(all_repo_data)} repositories from {num_pages} pages")
        
        # Now process the repository data in parallel
        all_repositories = []
        if all_repo_data:
            max_workers = min(200, len(all_repo_data))
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_repo = {
                    executor.submit(process_repo_data, repo_data): repo_data 
                    for repo_data in all_repo_data
                }
                
                for future in as_completed(future_to_repo):
                    repo_data = future_to_repo[future]
                    try:
                        result = future.result(timeout=30)
                        if result:
                            all_repositories.append(result)
                    except Exception as e:
                        logger.error(f"Failed to process repo {repo_data.get('name', 'unknown')}: {e}")
        
        # Cache the complete dataset
        try:
            cache.set(cache_key, all_repositories, timeout=CACHE_TIMEOUT_LONG)
            logger.debug(f"Cached {len(all_repositories)} repositories for user {user_id}")
        except Exception as e:
            logger.warning(f"Repository cache set failed: {e}")
        
        return all_repositories
        
    except Exception as e:
        logger.error(f"Failed to fetch repositories: {e}")
        raise

def sort_repositories_backend(repositories, sort='updated', table_sort=None, table_sort_direction='asc'):
    """Sort repositories on the backend from cached data"""
    # Make a copy to avoid modifying original cached data
    sorted_repos = repositories.copy()
    
    # Apply table sorting first if specified (overrides main sort)
    if table_sort:
        try:
            def get_sort_value(repo, field):
                value = repo.get(field)
                
                # Handle null/undefined values
                if value is None:
                    return ''
                
                # Special handling for different field types
                if field == 'name':
                    return value.lower() if value else ''
                elif field == 'language':
                    return value.lower() if value else ''
                elif field == 'updated_at':
                    return value  # ISO format strings sort correctly
                elif field in ['stargazers_count', 'forks_count', 'size']:
                    try:
                        return int(value) if value is not None else 0
                    except:
                        return 0
                else:
                    return value or ''
            
            sorted_repos.sort(
                key=lambda repo: get_sort_value(repo, table_sort),
                reverse=(table_sort_direction == 'desc')
            )
            return sorted_repos
        except Exception as e:
            logger.error(f"Error applying table sort {table_sort}: {e}")
    
    # Apply main sorting
    if sort == 'updated':
        sorted_repos.sort(key=lambda x: x['updated_at'] or '', reverse=True)
    elif sort == 'created':
        sorted_repos.sort(key=lambda x: x['created_at'] or '', reverse=True)
    elif sort == 'pushed':
        sorted_repos.sort(key=lambda x: x['pushed_at'] or '', reverse=True)
    elif sort == 'full_name':
        sorted_repos.sort(key=lambda x: x['full_name'].lower())
    
    return sorted_repos

def filter_repositories_backend(repositories, search_query=None):
    """Filter repositories on the backend from cached data"""
    if not search_query:
        return repositories
    
    search_query = search_query.strip().lower()
    if not search_query:
        return repositories
    
    filtered_repos = []
    for repo in repositories:
        repo_name = repo['name'].lower()
        repo_full_name = repo['full_name'].lower()
        repo_description = (repo['description'] or '').lower()
        
        if (search_query in repo_name or 
            search_query in repo_full_name or 
            search_query in repo_description):
            filtered_repos.append(repo)
    
    return filtered_repos

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
        search_query = request.args.get('search', '').strip().lower()
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 30)), 100)
        
        # Table sorting parameters
        table_sort = request.args.get('table_sort')
        table_sort_direction = request.args.get('table_sort_direction', 'asc')
        
        print(f"[DEBUG] Parameters - sort: {sort}, search: '{search_query}', page: {page}, per_page: {per_page}, table_sort: {table_sort}, table_sort_direction: {table_sort_direction}")
        
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
        
        print(f"[DEBUG] Fetching repositories using single cache method...")
        fetch_start = time.time()
        
        # Get all repositories from single cache
        all_repositories = get_all_user_repositories(access_token, user_id)
        
        # Apply search filter if needed
        if search_query:
            all_repositories = filter_repositories_backend(all_repositories, search_query)
        
        # Apply sorting (table sorting takes precedence)
        all_repositories = sort_repositories_backend(
            all_repositories, 
            sort=sort, 
            table_sort=table_sort, 
            table_sort_direction=table_sort_direction
        )
        
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
            'table_sort': table_sort,
            'table_sort_direction': table_sort_direction,
            'debug_info': {
                'processing_time': total_time,
                'fetch_time': fetch_time,
                'repos_total': len(all_repositories),
                'repos_returned': len(paginated_repos),
                'cache_enabled': True,
                'single_cache_strategy': True,
                'table_sort_applied': bool(table_sort)
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

@app.route('/api/following')
@cache_manager.cache_user_data('following', CACHE_TIMEOUT_MEDIUM)
def following():
    """Get the list of users that the authenticated user is following"""
    print(f"[DEBUG] /api/following called at {request.remote_addr}")
    
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
    user_login = user.get('login', 'unknown')
    print(f"[DEBUG] Getting following for user: {user_login}")
    
    try:
        g = Github(access_token)
        
        # Check rate limit
        if not check_rate_limit(g):
            return jsonify({'error': 'Rate limit too low, please try again later'}), 429
        
        # Get the authenticated user's following
        auth_user = g.get_user()
        following_users = []
        
        for user in auth_user.get_following():
            following_users.append({
                'id': user.id,
                'login': user.login,
                'avatar_url': user.avatar_url,
                'html_url': user.html_url,
                'type': user.type
            })
        
        print(f"[DEBUG] Found {len(following_users)} following users")
        return jsonify(following_users)
        
    except GithubException as e:
        error_msg = f'GitHub API error: {e.data.get("message", str(e)) if hasattr(e, "data") and e.data else str(e)}'
        print(f"[DEBUG] GithubException in following endpoint: {error_msg}")
        return jsonify({'error': error_msg}), getattr(e, 'status', 500)
    except Exception as e:
        error_msg = f'Failed to fetch following: {str(e)}'
        print(f"[DEBUG] Exception in following endpoint: {error_msg}")
        return jsonify({'error': error_msg}), 500

@app.route('/api/followers')
@cache_manager.cache_user_data('followers', CACHE_TIMEOUT_MEDIUM)
def followers():
    """Get the list of users that follow the authenticated user"""
    print(f"[DEBUG] /api/followers called at {request.remote_addr}")
    
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
    user_login = user.get('login', 'unknown')
    print(f"[DEBUG] Getting followers for user: {user_login}")
    
    try:
        g = Github(access_token)
        
        # Check rate limit
        if not check_rate_limit(g):
            return jsonify({'error': 'Rate limit too low, please try again later'}), 429
        
        # Get the authenticated user's followers
        auth_user = g.get_user()
        followers_list = []
        
        for user in auth_user.get_followers():
            followers_list.append({
                'id': user.id,
                'login': user.login,
                'avatar_url': user.avatar_url,
                'html_url': user.html_url,
                'type': user.type
            })
        
        print(f"[DEBUG] Found {len(followers_list)} followers")
        return jsonify(followers_list)
        
    except GithubException as e:
        error_msg = f'GitHub API error: {e.data.get("message", str(e)) if hasattr(e, "data") and e.data else str(e)}'
        print(f"[DEBUG] GithubException in followers endpoint: {error_msg}")
        return jsonify({'error': error_msg}), getattr(e, 'status', 500)
    except Exception as e:
        error_msg = f'Failed to fetch followers: {str(e)}'
        print(f"[DEBUG] Exception in followers endpoint: {error_msg}")
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
        # Get cache type to clear from request
        cache_type = request.json.get('cache_type') if request.json else None
        
        # Clear user-specific cache
        invalidate_user_cache(user_id, cache_type)
        
        message = f'Cache cleared successfully'
        if cache_type:
            message = f'{cache_type.title()} cache cleared successfully'
            
        return jsonify({'message': message})
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

@app.route('/api/debug/session')
def debug_session():
    """Debug endpoint to check session state"""
    return jsonify({
        'session_keys': list(session.keys()),
        'session_id': session.get('_id', 'NO_ID'),
        'cookies_received': dict(request.cookies),
        'user_in_session': 'user' in session,
        'session_permanent': session.permanent,
        'session_data': dict(session) if session else {}
    })

@app.route('/api/debug/test-session')
def test_session():
    """Test endpoint to set a simple session value"""
    session['test_value'] = 'test_data'
    session.permanent = True
    return jsonify({
        'message': 'Test session value set',
        'session_keys': list(session.keys()),
        'test_value': session.get('test_value')
    })

def process_repo_data(repo_data):
    """Process raw repository data from GitHub API"""
    try:
        # Topics might need a separate API call for some repos, but many repos include them
        topics = repo_data.get('topics', [])
        
        return {
            'id': repo_data.get('id'),
            'name': repo_data.get('name'),
            'full_name': repo_data.get('full_name'),
            'description': repo_data.get('description'),
            'private': repo_data.get('private', False),
            'html_url': repo_data.get('html_url'),
            'clone_url': repo_data.get('clone_url'),
            'ssh_url': repo_data.get('ssh_url'),
            'language': repo_data.get('language'),
            'stargazers_count': repo_data.get('stargazers_count', 0),
            'watchers_count': repo_data.get('watchers_count', 0),
            'forks_count': repo_data.get('forks_count', 0),
            'size': repo_data.get('size', 0),
            'default_branch': repo_data.get('default_branch'),
            'created_at': repo_data.get('created_at'),
            'updated_at': repo_data.get('updated_at'),
            'pushed_at': repo_data.get('pushed_at'),
            'archived': repo_data.get('archived', False),
            'disabled': repo_data.get('disabled', False),
            'fork': repo_data.get('fork', False),
            'topics': topics,
            'visibility': repo_data.get('visibility', 'private' if repo_data.get('private') else 'public'),
            'owner': {
                'login': repo_data.get('owner', {}).get('login'),
                'type': repo_data.get('owner', {}).get('type')
            }
        }
    except Exception as e:
        logger.error(f"Error processing repo data for {repo_data.get('name', 'unknown')}: {e}")
        return None

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
