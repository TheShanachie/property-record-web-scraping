"""
server

This package contains the main server logic, API routes, thread/driver pool managers,
and web scraping utilities for the application.
"""
# Import preliminary modules
from property_record_web_scraping.server.build import build_binaries

# Import Config for centralized path management
from property_record_web_scraping.server.config_utils import Config

# Set up paths using centralized Config system
Config.setup_python_path()  # Add src directory to Python path
project_root = Config.get_project_root()

# Build the project binaries if it is necessary.
build_binaries()
    
# Import the main server application, create it, then expose it.
from property_record_web_scraping.server.app import _create_app
def build(run_immediately: bool = False):
    """ 
    Build the application by ensuring all dependencies are ready and creating the Flask app.
    
    This method handles:
    - Path setup and configuration
    - Chrome and ChromeDriver installation if needed
    - Flask app creation
    
    Args:
        run_immediately (bool): If True, runs the Flask app immediately after creation
        
    Returns:
        Flask app instance
    """
    
    app = _create_app()
    if run_immediately:
        app.run()
    return app

# Expose the app and factory functions for use in other modules
__all__ = ['build']