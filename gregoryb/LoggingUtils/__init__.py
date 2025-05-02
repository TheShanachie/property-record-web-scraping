"""
Logging Module Initialization

This package provides a specialized logging utility for web scraping applications,
featuring a singleton logger with configurable logging mechanisms.

Package Components:
- WebScrapeLogger: A singleton logger class for consistent logging across web scraping projects
- RecordLogger: A singleton logger class for logging web scraping results to a MongoDB database

Key Features:
- Singleton design pattern
- Multiple logging levels (debug, info, warning, error, critical)
- Customizable logging configuration
- Thread-safe logging implementation
"""

# Import the submodules
from .Logger import WebScrapeLogger
from .ResultLogger import RecordLogger

# Expose key classes and create a default logger instance
__all__ = ['WebScrapeLogger', 'RecordLogger']



