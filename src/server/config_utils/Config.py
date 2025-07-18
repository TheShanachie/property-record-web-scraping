import yaml
import os

class Config:
    """
    Config.py
    This module provides a singleton `Config` class for managing application configuration
    using a YAML file. The configuration is loaded once and shared across the application.
    Classes:
        - Config: A singleton class to load and access configuration data.
    Usage:
        - To load the configuration:
            config = Config()
        - To access the entire configuration dictionary:
            config_data = Config.get_config()
        - To access a specific configuration value by key:
            value = Config.get('some_key')
    Methods:
        - __new__(cls, config_file='./ConfigUtils/config.yaml'):
            Ensures the `Config` class is a singleton. Loads the configuration file if the
            instance is created for the first time.
        - _load_config(self, config_file):
            Loads the YAML configuration file into a dictionary. Returns None if the file cannot be loaded.
        - 
    Attributes:
        - _instance: A class-level attribute to store the singleton instance.
        - _config: A dictionary to store the loaded configuration data.
    Dependencies:
        - os: Used to check the existence of the configuration file.
        - yaml: Used to parse the YAML configuration file.
    Exceptions:
        - FileNotFoundError: Raised if the specified configuration file does not exist.
    Note:
        - The default configuration file path is '...'
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._config = {}
            
            # Load the selenium chrome configuration data
            cls._config.update(cls._load_selenium_chrome_config())
            
            # Load the logging configuration data
            cls._config.update(cls._load_logging_config())
            
            # Load the dump database configuration data
            cls._config.update(cls._load_dump_database_config())
            
        return cls._instance
    
    @classmethod
    def _load_config(cls, config_file) -> dict: 
        """
        Load the configuration from a YAML file into a dictionary.
        Args:
            config_file (str): Path to the YAML configuration file.
        Returns:
            None if the file cannot be loaded, otherwise loads the configuration and returns a dictionary.
        Raises:
            FileNotFoundError: If the specified configuration file does not exist.
            Exception: If there is an error reading the configuration file.
        """
        loaded_config = None
        with open(config_file, 'r') as file:
            loaded_config = yaml.safe_load(file)
        return loaded_config
    
    @classmethod
    def _load_selenium_chrome_config(cls, config_path='./server/config/selenium_chrome.yaml'):
        """
        
        """
        instance = cls()
        return instance._load_config(config_path)
        
    @classmethod
    def _load_logging_config(cls, config_path='./server/config/logging.yaml'):
        """
        
        """
        instance = cls()
        return instance._load_config(config_path)
    
    @classmethod
    def _load_dump_database_config(cls, config_path='./server/config/dump_database.yaml'):
        """
        
        """
        instance = cls()
        return instance._load_config(config_path)
    
    @classmethod
    def get_config(cls):
        instance = cls()
        return instance._instance._config
    
    @classmethod
    def get(cls, key):
        instance = cls()
        return instance._instance._config[key]