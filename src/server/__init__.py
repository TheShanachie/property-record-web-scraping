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

# Add the project root to the system path if it's not already there
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
# Import the main server application, create it, then expise it.
from .app import _create_app
app = _create_app()

# Expose the app for use in other modules
__all__ = ['app']
