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
