"""
Authentication service using Strategy pattern for different OAuth providers
"""
import os
import requests
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from github import Github
from github.GithubException import GithubException
from models.user import User

logger = logging.getLogger(__name__)


class AuthenticationStrategy(ABC):
    """Abstract strategy for OAuth authentication"""
    
    @abstractmethod
    def get_auth_url(self, callback_url: str, scope: str) -> str:
        """Get OAuth authorization URL"""
        pass
    
    @abstractmethod
    def exchange_code_for_token(self, code: str) -> str:
        """Exchange authorization code for access token"""
        pass
    
    @abstractmethod
    def get_user_info(self, access_token: str) -> User:
        """Get user information using access token"""
        pass


class GitHubAuthStrategy(AuthenticationStrategy):
    """GitHub OAuth authentication strategy"""
    
    def __init__(self):
        self.client_id = os.environ.get('GITHUB_CLIENT_ID', 'your_client_id')
        self.client_secret = os.environ.get('GITHUB_CLIENT_SECRET', 'your_client_secret')
        self.auth_url = 'https://github.com/login/oauth/authorize'
        self.token_url = 'https://github.com/login/oauth/access_token'
    
    def get_auth_url(self, callback_url: str, scope: str = "read:user repo") -> str:
        """Get GitHub OAuth authorization URL"""
        return f"{self.auth_url}?client_id={self.client_id}&scope={scope}&redirect_uri={callback_url}"
    
    def exchange_code_for_token(self, code: str) -> str:
        """Exchange GitHub authorization code for access token"""
        try:
            response = requests.post(
                self.token_url,
                headers={'Accept': 'application/json'},
                data={
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'code': code
                },
                timeout=10
            )
            
            if response.status_code != 200:
                raise Exception(f"Token request failed with status {response.status_code}: {response.text}")
            
            token_json = response.json()
            access_token = token_json.get('access_token')
            
            if not access_token:
                raise Exception(f"No access token in response: {token_json}")
            
            return access_token
            
        except Exception as e:
            logger.error(f"Failed to exchange code for token: {e}")
            raise
    
    def get_user_info(self, access_token: str) -> User:
        """Get GitHub user information"""
        try:
            github_client = Github(access_token)
            github_user = github_client.get_user()
            
            # Get total repository count
            try:
                repo_list = github_user.get_repos()
                total_repos = repo_list.totalCount
            except Exception as e:
                logger.warning(f"Failed to fetch total repo count: {e}")
                total_repos = github_user.public_repos
            
            return User.from_github_user(github_user, total_repos)
            
        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            raise


class AuthenticationService:
    """Authentication service using Strategy pattern"""
    
    def __init__(self, strategy: AuthenticationStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: AuthenticationStrategy):
        """Change authentication strategy"""
        self._strategy = strategy
    
    def get_auth_url(self, callback_url: str, scope: str = None) -> str:
        """Get OAuth authorization URL"""
        if scope is None:
            scope = "read:user repo"  # Default GitHub scope
        return self._strategy.get_auth_url(callback_url, scope)
    
    def authenticate_user(self, code: str) -> tuple[str, User]:
        """Complete OAuth flow and return access token and user info"""
        try:
            # Exchange code for token
            access_token = self._strategy.exchange_code_for_token(code)
            
            # Get user information
            user = self._strategy.get_user_info(access_token)
            
            return access_token, user
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise
