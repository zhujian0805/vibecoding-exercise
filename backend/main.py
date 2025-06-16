"""
Refactored OAuth backend application using modern OOP design patterns
"""
import logging
from app_factory import ApplicationFactory

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def main():
    """Main application entry point"""
    try:
        # Create application using factory pattern
        app = ApplicationFactory.create_app()
        
        # Start the application
        from config import settings
        
        logger.info(f"Starting Flask app...")
        logger.info(f"Backend port: {settings.backend_port}")
        logger.info(f"Backend host: {settings.backend_host}")
        logger.info(f"Frontend URL: {settings.frontend_url}")
        logger.info(f"Callback URL: {settings.callback_url}")
        logger.info(f"GitHub Client ID: {settings.github_client_id[:8]}..." if settings.github_client_id != 'your_client_id' else "GitHub Client ID: NOT_SET")
        
        app.run(debug=True, host=settings.backend_host, port=settings.backend_port)
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise


if __name__ == '__main__':
    main()
