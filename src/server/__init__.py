"""
server

This package contains the main server logic, API routes, thread/driver pool managers,
and web scraping utilities for the application.
"""

from .routes import init_events_handler, scraping_bp

__all__ = [
    "init_events_handler",
    "scraping_bp",
]