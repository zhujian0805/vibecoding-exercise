"""
Authentication controller with proper error handling and validation
"""
import logging
from flask import Blueprint, request, redirect, session, jsonify
from services.auth_service import AuthenticationService, GitHubAuthStrategy
from config import settings

logger = logging.getLogger(__name__)


class AuthController:
    """Controller for authentication-related endpoints"""
    
    def __init__(self):
        self.auth_service = AuthenticationService(GitHubAuthStrategy())
        self.blueprint = Blueprint('auth', __name__)
        self._register_routes()
    
    def _register_routes(self):
        """Register all authentication routes"""
        self.blueprint.add_url_rule('/api/user', 'get_user', self.get_user, methods=['GET'])
        self.blueprint.add_url_rule('/api/login', 'login', self.login, methods=['GET'])
        self.blueprint.add_url_rule('/api/callback', 'callback', self.callback, methods=['GET'])
        self.blueprint.add_url_rule('/api/logout', 'logout', self.logout, methods=['POST'])
    
    def get_user(self):
        """Get current authenticated user"""
        logger.debug("get_user() called")
        logger.debug(f"Session keys: {list(session.keys())}")
        
        user = session.get('user')
        if user:
            response_data = {'authenticated': True, 'user': user}
            logger.debug(f"get_user() returning authenticated user: {user.get('login', 'unknown')}")
            return jsonify(response_data)
        
        response_data = {'authenticated': False}
        logger.debug("get_user() returning unauthenticated")
        return jsonify(response_data), 401
    
    def login(self):
        """Get OAuth authorization URL"""
        try:
            callback_url = settings.callback_url
            auth_url = self.auth_service.get_auth_url(callback_url)
            return jsonify({'auth_url': auth_url})
        except Exception as e:
            logger.error(f"Failed to generate login URL: {e}")
            return jsonify({'error': 'Failed to generate login URL'}), 500
    
    def callback(self):
        """Handle OAuth callback"""
        logger.debug(f"Callback called with args: {request.args}")
        logger.debug(f"Session before callback: {dict(session)}")
        
        code = request.args.get('code')
        error = request.args.get('error')
        
        if error:
            logger.error(f"OAuth error: {error}")
            return redirect(f"{settings.frontend_url}/login?error={error}")
        
        if not code:
            logger.error("No authorization code received")
            return redirect(f"{settings.frontend_url}/login?error=no_code")
        
        logger.debug(f"Received authorization code: {code[:10]}...")
        
        try:
            # Authenticate user using the service
            access_token, user = self.auth_service.authenticate_user(code)
            
            # Store user data and access token in session
            session['user'] = user.to_dict()
            session['access_token'] = access_token
            session.permanent = True
            
            logger.debug(f"OAuth callback completed for user: {user.login}")
            logger.debug(f"Session user set to: {session.get('user', {}).get('login', 'NOT_SET')}")
            
            # Redirect to frontend after successful authentication
            return redirect(f"{settings.frontend_url}/")
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return redirect(f"{settings.frontend_url}/login?error=auth_failed")
    
    def logout(self):
        """Logout user and clear session"""
        logger.debug("Logout called")
        
        user = session.get('user')
        if user:
            user_login = user.get('login', 'unknown')
            logger.debug(f"Logging out user: {user_login}")
        
        # Clear session
        session.clear()
        logger.debug("Session cleared")
        
        return jsonify({'message': 'Logged out successfully'})
