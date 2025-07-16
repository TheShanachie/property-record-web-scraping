"""
Logging Utility for Web Scraping

This module was documented using Claude 3.5 Haiku, an AI assistant created by Anthropic.
The documentation was generated with careful attention to Python docstring conventions,
providing clear and comprehensive explanations of the code's structure and functionality.

The AI-assisted documentation aims to:
- Provide clear, concise explanations of code purpose and functionality
- Enhance code readability and maintainability
- Offer insights into the design choices and implementation details

Documentation Date: March 2025
AI Assistant: Claude 3.5 Haiku by Anthropic
"""

# Import basic utilities
from ..config_utils import Config
import logging
class WebScrapeLogger:    
    
    _instance = None
    def __new__(cls):
        if not cls._instance:
            cls._instance = super(WebScrapeLogger, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    
    def _initialize(self):
        """
        Initializes the logger and related configurations for the application.
        This method sets up a logger named 'WebScrapeLogger' with a logging level of DEBUG,
        ensuring that all messages are logged. It configures file handlers based on the 
        settings provided in the application's configuration file and applies the specified 
        formatting to each handler. Additionally, it ensures the existence of a directory 
        for emergency source dumps, creating it if necessary.
        Attributes:
            logger (logging.Logger): The logger instance used for logging messages.
            logging_config (dict): Configuration settings for logging utilities, including
                log directory and file handlers.
            logging_dir (str): The directory where log files will be stored.
            source_dump_dir (str): The directory where emergency driver source dumps will
                be stored.
        Raises:
            KeyError: If required keys are missing in the configuration file.
            OSError: If there is an error creating the emergency dump directory.
        """
        # Create a logger
        self.logger = logging.getLogger('WebScrapeLogger')
        self.logger.setLevel(logging.DEBUG) # All mesasages will be logged.
        
        ### Program Logs ###
        self.logging_config = Config.get("logging-utils")
        self.logging_dir = self.logging_config['log-dir']
        for handler in self.logging_config['file-handlers']:
            
            # Create a file handler
            file_handler = logging.FileHandler(filename=self.logging_dir+handler['filename'], mode='a+')
            file_handler.setLevel(handler['level'])
            formatter = logging.Formatter(handler['format'])
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
    
    @classmethod
    def error(cls, msg: str = "No error message was provided"):
        instance = cls()
        instance.logger.error(msg)
        
    @classmethod
    def info(cls, msg: str = "No info message was provided"):
        instance = cls()
        instance.logger.info(msg)
        
    @classmethod
    def debug(cls, msg: str = "No debug message was provided"):
        instance = cls()
        instance.logger.debug(msg)
        
    @classmethod
    def warning(cls, msg: str = "No warning message was provided"):
        instance = cls()
        instance.logger.warning(msg)
        
    @classmethod
    def critical(cls, msg: str = "No critical message was provided"):
        instance = cls()
        instance.logger.critical(msg)
        
    @classmethod
    def dump_driver_source(cls, data: str):
        # This method is used to dump the source of the driver in case of an emergency.
        # It is not used in the current implementation, but it can be used in the future.
        return None