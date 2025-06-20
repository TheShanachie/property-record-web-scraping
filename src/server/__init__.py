"""
server

This package contains the main server logic, API routes, thread/driver pool managers,
and web scraping utilities for the application.
"""

from .routes import init_thread_pool, init_driver_pool, scraping_bp, create_json_response
from .thread_pool_manager import WebScrapingThreadPool, TaskData
from .driver_pool import DriverPool

# Optionally, expose the web_scraping_utils submodule for convenience
from . import web_scraping_utils

__all__ = [
    "init_thread_pool",
    "init_driver_pool",
    "scraping_bp",
    "create_json_response",
    "WebScrapingThreadPool",
    "TaskData",
    "DriverPool"
]