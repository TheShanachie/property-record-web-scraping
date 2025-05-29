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
        - read_config(cls, config_file='./ConfigUtils/config.yaml'):
            Reloads the configuration from a new YAML file, overwriting any previous configuration.
        - get_config(cls):
            Returns the entire configuration dictionary.
        - get(cls, key):
            Returns the value associated with the specified key in the configuration.
    Attributes:
        - _instance: A class-level attribute to store the singleton instance.
        - _config: A dictionary to store the loaded configuration data.
    Dependencies:
        - os: Used to check the existence of the configuration file.
        - yaml: Used to parse the YAML configuration file.
    Exceptions:
        - FileNotFoundError: Raised if the specified configuration file does not exist.
    Note:
        - The default configuration file path is './config_utils/config.yaml'. This can be
          overridden by passing a different path when creating the `Config` instance. One 
          may also use the `read_config` method to load a different configuration file.
    """
    _instance = None

    def __new__(cls, config_file='./config_utils/config.yaml'):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config(config_file)
        return cls._instance

    def _load_config(self, config_file):
        try:
            with open(config_file, 'r') as file:
                self._config = yaml.safe_load(file)
        except:
            # Could not load config details from the path provided.
            return None
            
    @classmethod
    def read_config(cls, config_file='./ConfigUtils/config.yaml'):
        """
        Overwrite any previous configuration details which have been loaded into the class.
        This method attempts to read from a new configuration 'yaml' file.       
        """
        cls._instance = super(Config, cls).__new__(cls)
        cls._instance._load_config(config_file)
    
    @classmethod
    def get_config(cls):
        instance = cls()
        return instance._instance._config
    
    @classmethod
    def get(cls, key):
        instance = cls()
        return instance._instance._config[key]