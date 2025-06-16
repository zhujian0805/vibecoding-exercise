import os

class Settings:
    def __init__(self):
        self.flask_secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_secret_key')
        self.cache_type = os.environ.get('CACHE_TYPE', 'simple')
        self.cache_default_timeout = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', '3600'))
        self.redis_url = os.environ.get('REDIS_URL', None)
        self.redis_host = os.environ.get('REDIS_HOST', None)
        self.github_client_id = os.environ.get('GITHUB_CLIENT_ID', 'your_client_id')
        self.github_client_secret = os.environ.get('GITHUB_CLIENT_SECRET', 'your_client_secret')
        self.frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost')
        self.backend_host = os.environ.get('BACKEND_HOST', 'localhost')
        self.backend_port = int(os.environ.get('BACKEND_PORT', '5000'))
        self.callback_url = os.environ.get('CALLBACK_URL') or f"http://{self.backend_host}:{self.backend_port}/api/callback"

settings = Settings()
