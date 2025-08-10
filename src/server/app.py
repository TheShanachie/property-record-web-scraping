from server.routes import scraping_bp, init_events_handler
# from server.server_cleanup import ProcessCleanupManager
from server.config_utils.Config import Config
from flask import Flask
import atexit, os

def _configure_flask_app():
    """
    Configure and create the Flask application instance.
    
    Returns:
        Flask: Configured Flask app instance
    """
    # Load app-specific config
    flask_config = Config.get_config("flask_app")  # e.g., {"HOST": "127.0.0.1", "PORT": 5001}
    host = flask_config.get("HOST", "127.0.0.1")
    port = flask_config.get("PORT", 5000)

    # Create the Flask app instance
    app = Flask(__name__)
    app.config.update(flask_config)

    # Derive and store base URL
    app.config["BASE_URL"] = f"http://{host}:{port}"
    
    return app

def _setup_events_handler():
    """
    Initialize and register the events handler.
    
    Returns:
        EventsHandler: Initialized events handler instance
    """
    
    def _cleanup_garbage_chrome():
        """ Cleanup garbage chrome processes that are left behind. """
        os.system("pkill -f chrome")
    
    # Initialize the events handler
    events_handler = init_events_handler(
        **Config.get_config("events_handler_init")
    )

    # Register cleanup
    atexit.register(_cleanup_garbage_chrome)
    atexit.register(events_handler.shutdown)
    
    return events_handler


def _override_run_method(app):
    """
    Override the Flask app's run method to use config defaults.
    
    Args:
        app (Flask): Flask application instance
    """
    # Store original run method
    _original_run = app.run
    
    def custom_run(host=None, port=None, debug=None, **options):
        """Override run method to use config defaults"""
        
        # Use config values as defaults if not provided
        host = host or app.config.get("HOST", "127.0.0.1")
        port = port or app.config.get("PORT", 5000)
        debug = debug if debug is not None else app.config.get("DEBUG", False)
        
        return _original_run(host=host, port=port, debug=debug, **options)
    
    # Replace the run method
    app.run = custom_run

def _register_blueprints(app):
    """
    Register all application blueprints.
    
    Args:
        app (Flask): Flask application instance
    """
    # Register blueprints
    app.register_blueprint(scraping_bp, url_prefix='/api/v1')

def _create_app():
    """
    Create and configure the Flask application. Return a ready-to-use Flask app instance.
    This function is intended to be called in the server module __init__.py file. There are 
    a number of relative dependencies that need to be resolved before the app can be created.        
    """
    # Configure Flask app
    app = _configure_flask_app()
    
    # Setup events handler
    _setup_events_handler()
    
    # Register blueprints
    _register_blueprints(app)
    
    # Override run method to use config defaults
    _override_run_method(app)

    return app