# Import basic utilities
from property_record_web_scraping.server.config_utils import Config
import logging, os

def _create_logger(name: str, config_key: str) -> logging.Logger:
    """
    Create a logger with the specified name and configuration key.
    This will set up a new logger instance with file handlers based 
    on the project configuration
    
    Args:
        name (str): The name of the logger.
        config_key (str): The configuration key to retrieve logging settings.
    
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Set the logger to DEBUG level
    config = Config.get_config(['logging_utils', 'loggers', config_key])
    logdir = Config.get_config(['logging_utils', 'log-dir'])
    os.makedirs(logdir, exist_ok=True)  # Ensure the log directory exists
    logger.propagate = False  # Prevent propagation to root logger
    
    if config.get('silent', False): 
        # Create a dummy logger if silent mode is enabled
        dummy_logger = logging.getLogger('silent_logger')
        dummy_logger.addHandler(logging.NullHandler())
        dummy_logger.propagate = False
        return dummy_logger
    
    for handler in config['file-handlers']:
        
        # If not silent, create an actual loggers
        level = getattr(logging, handler['level'].upper(), logging.DEBUG) # Default to DEBUG if level is not found
        filename = os.path.join(logdir, handler['filename'])
        file_handler = logging.FileHandler(filename=filename, mode='a+')
        file_handler.setLevel(level)
        formatter = logging.Formatter(handler['format'])
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # log a quick debug message to indicate the logger is set up
        logger.debug(f"Logger '{name}' initialized with file handler '{filename}' at level '{handler['level']}'")
    
    return logger

# 1. create a logger for 'web_scraping_core', use config to create
web_scraping_core_logger = _create_logger('web_scraping_core', 'web_scraping_core')

# 2. create a logger for 'flask_app_interactions', use config to create
flask_app_interactions_logger = _create_logger('flask_app_interactions', 'flask_app_interactions')

# 3. create a logger for 'event_handling_operations', use config to create
event_handling_operations_logger = _create_logger('event_handling_operations', 'event_handling_operations')

# 4. create a logger for 'resource_management', use config to create
resource_management_logger = _create_logger('resource_management', 'resource_management')



# class Logger:
#     """
#     This class provides a singleton logger for the web scraping application.
#     It initializes the logger with specific configurations and provides methods
#     to log messages at different levels (error, info, debug, warning, critical).
#     This logger class is designed to be inherited by other logging classes for
#     specific needs. 
#     """
    
#     _instance = None
#     def __new__(cls):
#         if not cls._instance:
#             cls._instance = super(Logger, cls).__new__(cls)
#             cls._instance._initialize()
#         return cls._instance
    
    

# class WebScrapeLogger:    
    
#     _instance = None
#     def __new__(cls):
#         if not cls._instance:
#             cls._instance = super(WebScrapeLogger, cls).__new__(cls)
#             cls._instance._initialize()
#         return cls._instance
    
    
#     def _initialize(self):
#         """
#         Initializes the logger and related configurations for the application.
#         This method sets up a logger named 'WebScrapeLogger' with a logging level of DEBUG,
#         ensuring that all messages are logged. It configures file handlers based on the 
#         settings provided in the application's configuration file and applies the specified 
#         formatting to each handler. Additionally, it ensures the existence of a directory 
#         for emergency source dumps, creating it if necessary.
#         Attributes:
#             logger (logging.Logger): The logger instance used for logging messages.
#             logging_config (dict): Configuration settings for logging utilities, including
#                 log directory and file handlers.
#             logging_dir (str): The directory where log files will be stored.
#             source_dump_dir (str): The directory where emergency driver source dumps will
#                 be stored.
#         Raises:
#             KeyError: If required keys are missing in the configuration file.
#             OSError: If there is an error creating the emergency dump directory.
#         """
#         # Create a logger
#         self.logger = logging.getLogger('WebScrapeLogger')
#         self.logger.setLevel(logging.DEBUG) # All mesasages will be logged.
        
#         ### Program Logs ###
#         self.logging_config = Config.get_config("logging_utils")
#         self.logging_dir = self.logging_config['log-dir']
#         for handler in self.logging_config['file-handlers']:
            
#             # Create a file handler
#             file_handler = logging.FileHandler(filename=self.logging_dir+handler['filename'], mode='a+')
#             file_handler.setLevel(handler['level'])
#             formatter = logging.Formatter(handler['format'])
#             file_handler.setFormatter(formatter)
#             self.logger.addHandler(file_handler)
        
    
#     @classmethod
#     def error(cls, msg: str = "No error message was provided"):
#         instance = cls()
#         instance.logger.error(msg)
        
#     @classmethod
#     def info(cls, msg: str = "No info message was provided"):
#         instance = cls()
#         instance.logger.info(msg)
        
#     @classmethod
#     def debug(cls, msg: str = "No debug message was provided"):
#         instance = cls()
#         instance.logger.debug(msg)
        
#     @classmethod
#     def warning(cls, msg: str = "No warning message was provided"):
#         instance = cls()
#         instance.logger.warning(msg)
        
#     @classmethod
#     def critical(cls, msg: str = "No critical message was provided"):
#         instance = cls()
#         instance.logger.critical(msg)
        
#     @classmethod
#     def dump_driver_source(cls, data: str):
#         # This method is used to dump the source of the driver in case of an emergency.
#         # It is not used in the current implementation, but it can be used in the future.
#         return None