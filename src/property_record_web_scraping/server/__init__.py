"""
server

This package contains the main server logic, API routes, thread/driver pool managers,
and web scraping utilities for the application.
"""
# Import preliminary modules
from property_record_web_scraping.server.build import install_chrome_and_driver_fixed_dirs

# Import Config for centralized path management
from property_record_web_scraping.server.config_utils import Config

# Set up paths using centralized Config system
Config.setup_python_path()  # Add src directory to Python path
project_root = Config.get_project_root()

# Build the project binaries if it is necessary.

# Use centralized build directory resolution
build_dir = Config.get_build_dir()

# Create build directory if it doesn't exist
build_dir.mkdir(parents=True, exist_ok=True)

install_chrome_and_driver_fixed_dirs(
    chrome_url="https://storage.googleapis.com/chrome-for-testing-public/138.0.7201.0/linux64/chrome-linux64.zip",
    driver_url="https://storage.googleapis.com/chrome-for-testing-public/138.0.7201.0/linux64/chromedriver-linux64.zip",
    build_dir=str(build_dir),
    check_exists=True,
    overwrite=True,
)
    
# Python path already set up by Config.setup_python_path() above
    
# Import the main server application, create it, then expose it.
from property_record_web_scraping.server.app import _create_app
app = _create_app()

# Expose the app for use in other modules
__all__ = ['app']