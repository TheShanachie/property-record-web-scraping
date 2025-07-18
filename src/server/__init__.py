"""
server

This package contains the main server logic, API routes, thread/driver pool managers,
and web scraping utilities for the application.
"""
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
from server.routes import init_events_handler, scraping_bp

__all__ = [
    "init_events_handler",
    "scraping_bp",
]