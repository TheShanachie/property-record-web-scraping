"""
server

This package contains the main server logic, API routes, thread/driver pool managers,
and web scraping utilities for the application.
"""
# Import preliminary modules
import sys
import os

# Get the project root direcrtory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Build the project binaries if it is necessary.
from .build import install_chrome_and_driver_fixed_dirs
build_dir = os.path.join(project_root, "server", "build", "bin")
install_chrome_and_driver_fixed_dirs(
    chrome_url="https://storage.googleapis.com/chrome-for-testing-public/138.0.7201.0/linux64/chrome-linux64.zip",
    driver_url="https://storage.googleapis.com/chrome-for-testing-public/138.0.7201.0/linux64/chromedriver-linux64.zip",
    build_dir=build_dir,
    check_exists=True,
    overwrite=True,
)
    
# Add the project root to the system path if it's not already there
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
# Import the main server application, create it, then expise it.
from server.app import _create_app
app = _create_app()

# Expose the app for use in other modules
__all__ = ['app']
