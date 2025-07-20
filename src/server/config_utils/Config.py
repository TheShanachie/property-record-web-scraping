import yaml
import os

class Config:
    """
    Config.py
    This module provides a singleton `Config` class for managing application configuration
    using a YAML file. The configuration is loaded once and shared across the application.
     
    Classes:
        - Config: A singleton class to load and access configuration data.
    Methods:
        - 
    Attributes:
        - _instance: A class-level attribute to store the singleton instance.
        - _config: A dictionary to store the loaded configuration data.
    Dependencies:
        - os: Used to check the existence of the configuration file.
        - yaml: Used to parse the YAML configuration file.
    Note:
        - The default configuration file path is '...'

    TODO: Add an in-memory flag to indicate whether we want to load the configuration in memory or not. Otherwise, we can technically read the configuration directly from the YAML file each time we need it.
    """
    _instance = None

    def __new__(cls):
        """
        Create a new instance of the Config class if it does not already exist.
        If an instance already exists, return the existing instance.
        """
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._config = {}
        return cls._instance
    
    @classmethod
    def initialize(cls, source: str | list | None = None) -> None:
        """
        Initialize the configuration by loading it from a specified source. If the configuration is 
        already loaded, this method will overwrite the existing configuration with the new one.
        The source can be a single YAML file, a list of YAML files, or a directory containing YAML files.
        If no source is provided, it defaults to loading from the 'config' directory.

        Args:
            source (str | list | None): Path to a single YAML file, a list of YAML file paths, or a directory path.
        
        Raises:
            FileNotFoundError: If the specified file or directory does not exist.
            Exception: If there is an error reading any of the configuration files.
        """
        if isinstance(source, str):
            if os.path.isdir(source):
                cls._instance._config = cls._load_config_from_dir(source)
            elif os.path.isfile(source) and source.endswith('.yaml'):
                cls._instance._config = cls._load_config_from_file(source)
            else:
                raise ValueError(f"Invalid source: {source}. It should be a YAML file or a directory containing YAML files.")
        elif isinstance(source, list):
            cls._instance._config = cls._load_config_from_list(source)
        elif source is None:
            # Default to loading from the 'config' directory
            cls._instance._config = cls._load_config_from_dir('./server/config')
        else:
            raise ValueError("Source must be a string (file path), a list of file paths, or None.")
    
    @classmethod
    def _load_config_from_list(cls, config_list: list) -> dict:
        """
        Load configuration from a list of YAML file paths into a dictionary.
        Args:
            config_list (list): List of paths to YAML configuration files.
        Returns:
            A dictionary containing the merged configuration from all YAML files in the list.
        Raises:
            FileNotFoundError: If any of the specified files do not exist.
            Exception: If there is an error reading any of the configuration files.
        """
        config = {}
        for config_file in config_list:
            if not os.path.exists(config_file):
                raise FileNotFoundError(f"Configuration file '{config_file}' does not exist.")
            file_name_without_ext = os.path.splitext(os.path.basename(config_file))[0]
            config[file_name_without_ext] = cls._load_config(config_file)
        return config

    @classmethod
    def _load_config_from_dir(cls, config_dir: str) -> dict:
        """
        Load all YAML configuration files from a specified directory into a dictionary.
        Args:
            config_dir (str): Path to the directory containing YAML configuration files.
        Returns:
            A dictionary containing the merged configuration from all YAML files in the directory.
        Raises:
            FileNotFoundError: If the specified directory does not exist.
            Exception: If there is an error reading any of the configuration files.
        """
        if not os.path.exists(config_dir):
            raise FileNotFoundError(f"Configuration directory '{config_dir}' does not exist.")

        config = {}
        for filename in os.listdir(config_dir):
            if filename.endswith('.yaml'):
                file_path = os.path.join(config_dir, filename)
                file_name_without_ext = os.path.splitext(filename)[0]
                config[file_name_without_ext] = cls._load_config(file_path)
        return config

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
    def get_config(cls, key: str | list = None) -> dict:
        """
        Get the entire configuration dictionary or a specific branch of it described by `key`.
        `key` may be either a list, string, or None. If key is None, the entire configuration is returned.
        If `key` is a string, then it is used to return a portion of the configuration. If key is a list, 
        then it is used to traverse the configuration dictionary. This will start with the first key in
        the list and traverse the configuration dictionary until it reaches the end of the list. If any key
        in the list or as a string is not found in the configuration, a KeyError is raised.

        Args:
            key (list or str, optional): A list of keys to traverse the configuration dictionary or a single key as a string.

        Returns:
            dict: The entire configuration dictionary or a specific branch of it.

        Raises:
            KeyError: If any key in the list or as a string is not found in the configuration.
        """
        instance = cls()
        if key is None:
            return instance._instance._config
        else:
            config = instance._instance._config
            if isinstance(key, str):
                key = [key]
            for k in key:
                if k in config:
                    config = config[k]
                else:
                    raise KeyError(f"Key '{k}' not found in configuration.")
            return config
