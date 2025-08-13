import yaml, os, json, sys
from pathlib import Path
from typing import Union, Optional

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
    _config = None
    _project_root: Optional[Path] = None
    _package_root: Optional[Path] = None

    def __new__(cls):
        """
        Create a new instance of the Config class if it does not already exist.
        If an instance already exists, return the existing instance.
        """
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._config = {}
        return cls._instance
    
    # === CENTRALIZED PATH MANAGEMENT METHODS ===
    
    @classmethod
    def get_project_root(cls) -> Path:
        """
        Get the project root directory (contains pyproject.toml).
        This is the single source of truth for project root calculation.
        
        Returns:
            Path: Absolute path to project root
        """
        if cls._project_root is not None:
            return cls._project_root
            
        # Try environment variable first (highest priority)
        if 'PROJECT_ROOT' in os.environ:
            cls._project_root = Path(os.environ['PROJECT_ROOT']).absolute()
            if cls._validate_project_root(cls._project_root):
                return cls._project_root
        
        # Calculate from this file location (Config.py)
        current_file = Path(__file__).absolute()
        # This file is at: src/property_record_web_scraping/server/config_utils/Config.py
        # Go up: config_utils -> server -> property_record_web_scraping -> src -> project_root
        cls._project_root = current_file.parent.parent.parent.parent.parent
        
        # Validate calculation
        if not cls._validate_project_root(cls._project_root):
            # Fallback: search upward for pyproject.toml
            cls._project_root = cls._find_project_root_upward(current_file)
        
        # Ensure environment variable is set for other components
        os.environ['PROJECT_ROOT'] = str(cls._project_root)
        return cls._project_root
    
    @classmethod
    def _validate_project_root(cls, path: Path) -> bool:
        """Validate that a path is the correct project root."""
        return path.exists() and (path / "pyproject.toml").exists()
    
    @classmethod
    def _find_project_root_upward(cls, start_path: Path) -> Path:
        """Search upward from start_path to find directory containing pyproject.toml."""
        current = start_path.parent
        while current.parent != current:  # Stop at filesystem root
            if (current / "pyproject.toml").exists():
                return current
            current = current.parent
        
        # If not found, use package directory as fallback
        return cls.get_package_root()
    
    @classmethod
    def get_package_root(cls) -> Path:
        """
        Get the package root directory.
        
        This file is always located at: property_record_web_scraping/server/config_utils/Config.py
        Go up 3 levels: config_utils -> server -> property_record_web_scraping
        
        Works in both development (src/) and installed (site-packages/) environments.
        """
        if cls._package_root is not None:
            return cls._package_root
            
        current_file = Path(__file__).absolute()
        # Go up: config_utils -> server -> property_record_web_scraping
        cls._package_root = current_file.parent.parent.parent
        return cls._package_root
    
    @classmethod
    def get_src_root(cls) -> Path:
        """Get the src directory."""
        return cls.get_project_root() / "src"
    
    @classmethod
    def setup_python_path(cls) -> None:
        """Add src directory to Python path if not already present."""
        src_path = str(cls.get_src_root())
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
    
    @classmethod
    def resolve_path(cls, path: Union[str, Path]) -> Path:
        """
        Universal path resolver that handles all path types.
        
        This method should be used by all components needing path resolution.
        All relative paths are resolved from the package root for uniform behavior
        between development and packaged environments.
        
        Args:
            path: Can be:
                - Absolute path (starts with /)
                - Relative path (starts with ./ or plain relative)
        
        Returns:
            Path: Absolute resolved path
        """
        if isinstance(path, Path):
            path = str(path)
            
        if path.startswith('/'):
            # Already absolute
            return Path(path)
        elif path.startswith('./'):
            # All relative paths resolve from package root
            return cls.get_package_root() / path[2:]
        else:
            # Plain relative path - assume from package root
            return cls.get_package_root() / path
    
    @classmethod
    def get_build_dir(cls) -> Path:
        """Get the build directory. Always uses package root for uniform behavior."""
        return cls.get_package_root() / "server" / "build" / "bin"
    
    @classmethod
    def get_config_dir(cls) -> Path:
        """Get the config directory."""
        return cls.get_package_root() / "server" / "config"
    
    @classmethod
    def get_logs_dir(cls) -> Path:
        """Get the logs directory."""
        return cls.get_package_root() / "server" / "logs"
    
    # === ENHANCED EXISTING METHODS ===
    
    @classmethod
    def _resolve_relative_path(cls, path: str) -> str:
        """
        Resolve a relative path to an absolute path.
        Now uses the centralized path resolver.
        """
        return str(cls.resolve_path(path))

    @classmethod
    def _resolve_paths_where_possible(cls, config: dict) -> dict:
        """
        Recursively resolve relative paths in the configuration dictionary.
        Only processes keys ending with '-path' or '_path' for explicit path resolution.
        Args:
            config (dict): The configuration dictionary to process.
        Returns:
            dict: The configuration dictionary with resolved paths.
        """
        for key, value in config.items():
            if isinstance(value, dict):
                config[key] = cls._resolve_paths_where_possible(value)
            elif isinstance(value, str) and (key.endswith('-path') or key.endswith('_path')):
                config[key] = cls._resolve_relative_path(value)
            # If the value is not a string or dict, we leave it as is.
            # print(json.dumps({key: value}, indent=2))  # Debugging output to see resolved paths
        return config

    @classmethod
    def initialize(cls, source: str | list | None = None, force_reload: bool = False) -> None:
        """
        Initialize the configuration by loading it from a specified source. 
        This method is idempotent - safe to call multiple times.
        
        Args:
            source (str | list | None): Path to a single YAML file, a list of YAML file paths, or a directory path.
            force_reload (bool): If True, force reload even if already initialized.
        
        Raises:
            FileNotFoundError: If the specified file or directory does not exist.
            Exception: If there is an error reading any of the configuration files.
        """
        
        # Check if already initialized (singleton behavior)
        if cls._config and not force_reload:
            return  # Already initialized, don't reload
        
        # Ensure we have a singleton instance
        cls._instance = cls()
        if isinstance(source, str):
            if os.path.isdir(source):
                cls._config = cls._load_config_from_dir(source)
            elif os.path.isfile(source) and source.endswith('.yaml'):
                cls._config = cls._load_config_from_file(source)
            else:
                raise ValueError(f"Invalid source: {source}. It should be a YAML file or a directory containing YAML files.")
        elif isinstance(source, list):
            cls._config = cls._load_config_from_list(source)
        elif source is None:
            # Default to loading from the 'config' directory
            config_dir = cls.get_config_dir()
            if config_dir.exists():
                cls._config = cls._load_config_from_dir(str(config_dir))
            else:
                cls._config = {}
        else:
            raise ValueError("Source must be a string (file path), a list of file paths, or None.")
        
        # Resolve paths in the configuration
        cls._config = cls._resolve_paths_where_possible(cls._config)
    
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
        # Lazy initialization - initialize if not already done
        if not cls._config:
            cls.initialize()
            
        instance = cls()
        if key is None:
            return instance._config
        else:
            config = instance._config
            if isinstance(key, str):
                key = [key]
            for k in key:
                if k in config:
                    config = config[k]
                else:
                    raise KeyError(f"Key '{k}' not found in configuration.")
            return config
