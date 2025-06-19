"""
Application factory with dependency injection and proper configuration
"""
import os
import logging
from flask import Flask
from flask_cors import CORS
from flask_caching import Cache
from config import settings
from services.cache_service import CacheManager
from controllers.auth_controller import AuthController
from controllers.repository_controller import RepositoryController
from controllers.gist_controller import GistController

logger = logging.getLogger(__name__)


class ApplicationFactory:
    """Factory for creating Flask application with proper configuration"""
    
    @staticmethod
    def create_app() -> Flask:
        """Create and configure Flask application"""
        app = Flask(__name__)
        
        # Configure application
        ApplicationFactory._configure_app(app)
        
        # Initialize cache
        cache = ApplicationFactory._setup_cache(app)
        
        # Initialize services
        cache_manager = CacheManager(cache)
        
        # Register controllers
        ApplicationFactory._register_controllers(app, cache_manager)
        
        # Setup additional routes
        ApplicationFactory._setup_additional_routes(app, cache_manager)
        
        return app
    
    @staticmethod
    def _configure_app(app: Flask):
        """Configure Flask application settings"""
        app.secret_key = settings.flask_secret_key
        
        # Configure session settings for proper cookie handling
        app.config.update(
            SESSION_COOKIE_HTTPONLY=False,   # Allow JavaScript access
            SESSION_COOKIE_SAMESITE='Lax',   # Allow cross-site requests for OAuth
            SESSION_COOKIE_SECURE=False,     # Set to True in production with HTTPS
            SESSION_COOKIE_DOMAIN='localhost',  # Share cookies across localhost
            SESSION_COOKIE_PATH='/',         # Make cookies available to all paths
            PERMANENT_SESSION_LIFETIME=3600  # 1 hour
        )
        
        # Configure CORS
        CORS(app, 
             supports_credentials=True, 
             origins=['http://localhost', 'http://localhost:80', 'http://localhost:3000', 
                     'http://127.0.0.1', 'http://127.0.0.1:80'],
             allow_headers=['Content-Type', 'Authorization', 'Cookie'],
             expose_headers=['Set-Cookie'],
             methods=['GET', 'POST', 'OPTIONS'])
    
    @staticmethod
    def _setup_cache(app: Flask) -> Cache:
        """Setup caching configuration"""
        cache_config = {
            'CACHE_TYPE': settings.cache_type,
            'CACHE_DEFAULT_TIMEOUT': settings.cache_default_timeout,
        }
        
        # Redis configuration if available
        if settings.redis_url:
            cache_config.update({
                'CACHE_TYPE': 'redis',
                'CACHE_REDIS_URL': settings.redis_url,
            })
        elif settings.redis_host:
            cache_config.update({
                'CACHE_TYPE': 'redis',
                'CACHE_REDIS_HOST': settings.redis_host,
                'CACHE_REDIS_PORT': 6379,
                'CACHE_REDIS_DB': 0,
            })
        
        cache = Cache(app, config=cache_config)
        logger.debug(f"Cache configured with type: {cache_config.get('CACHE_TYPE')}")
        
        return cache
    
    @staticmethod
    def _register_controllers(app: Flask, cache_manager: CacheManager):
        """Register all controllers with the application"""
        # Authentication controller
        auth_controller = AuthController()
        app.register_blueprint(auth_controller.blueprint)
        
        # Repository controller
        repo_controller = RepositoryController(cache_manager)
        app.register_blueprint(repo_controller.blueprint)
        
        # Gist controller
        gist_controller = GistController(cache_manager)
        app.register_blueprint(gist_controller.blueprint)
    
    @staticmethod
    def _setup_additional_routes(app: Flask, cache_manager: CacheManager):
        """Setup additional utility routes"""
        from flask import jsonify, request, session
        from github import Github
        
        @app.route('/api/profile')
        @cache_manager.cache_user_data('profile', 3600)
        def profile():
            """Get detailed user profile"""
            if 'user' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            access_token = session.get('access_token')
            if not access_token:
                return jsonify({'error': 'No access token'}), 401
            
            try:
                github_client = Github(access_token)
                user = github_client.get_user()
                
                # Get total repository count
                try:
                    repo_list = user.get_repos()
                    total_repos = repo_list.totalCount
                except Exception as e:
                    logger.warning(f"Failed to fetch total repo count: {e}")
                    total_repos = user.public_repos
                
                # Get total gist count
                try:
                    gist_list = user.get_gists()
                    total_gists = gist_list.totalCount
                except Exception as e:
                    logger.warning(f"Failed to fetch total gist count: {e}")
                    total_gists = 0
                
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
                    'total_gists': total_gists,
                    'followers': user.followers,
                    'following': user.following,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'updated_at': user.updated_at.isoformat() if user.updated_at else None,
                    'html_url': user.html_url
                }
                
                return jsonify(user_info)
                
            except Exception as e:
                return jsonify({'error': f'Failed to fetch user information: {str(e)}'}), 500
        
        @app.route('/api/followers')
        @cache_manager.cache_user_data('followers', 3600)
        def followers():
            """Get user followers"""
            if 'user' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            access_token = session.get('access_token')
            if not access_token:
                return jsonify({'error': 'No access token'}), 401
            
            try:
                github_client = Github(access_token)
                auth_user = github_client.get_user()
                
                followers_list = []
                for user in auth_user.get_followers():
                    followers_list.append({
                        'id': user.id,
                        'login': user.login,
                        'avatar_url': user.avatar_url,
                        'html_url': user.html_url,
                        'type': user.type
                    })
                
                return jsonify(followers_list)
                
            except Exception as e:
                return jsonify({'error': f'Failed to fetch followers: {str(e)}'}), 500
        
        @app.route('/api/following')
        @cache_manager.cache_user_data('following', 3600)
        def following():
            """Get users that the authenticated user is following"""
            if 'user' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            access_token = session.get('access_token')
            if not access_token:
                return jsonify({'error': 'No access token'}), 401
            
            try:
                github_client = Github(access_token)
                auth_user = github_client.get_user()
                
                following_users = []
                for user in auth_user.get_following():
                    following_users.append({
                        'id': user.id,
                        'login': user.login,
                        'avatar_url': user.avatar_url,
                        'html_url': user.html_url,
                        'type': user.type
                    })
                
                return jsonify(following_users)
                
            except Exception as e:
                return jsonify({'error': f'Failed to fetch following: {str(e)}'}), 500
        
        @app.route('/api/health')
        def health():
            """Health check endpoint"""
            return jsonify({'status': 'ok'})
        
        @app.route('/api/cache/status')
        def cache_status():
            """Get cache configuration and status"""
            if 'user' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            try:
                cache_info = cache_manager.get_cache_info()
                return jsonify({
                    'cache_timeout_short': 60,
                    'cache_timeout_medium': 3600,
                    'cache_timeout_long': 3600,
                    **cache_info
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
                cache_type = request.json.get('cache_type') if request.json else None
                cache_manager.invalidate_user_cache(user_id, cache_type)
                
                message = 'Cache cleared successfully'
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
                cache_manager.clear_all()
                return jsonify({'message': 'All cache cleared successfully'})
            except Exception as e:
                return jsonify({'error': f'Failed to clear all cache: {str(e)}'}), 500
        
        @app.route('/api/config')
        def config():
            """Get application configuration"""
            cache_info = cache_manager.get_cache_info()
            
            return jsonify({
                'callback_url': settings.callback_url,
                'frontend_url': settings.frontend_url,
                'backend_port': settings.backend_port,
                'github_client_id': settings.github_client_id[:8] + '...' if settings.github_client_id != 'your_client_id' else 'NOT_SET',
                'cache_type': cache_info.get('cache_type', 'unknown')
            })
