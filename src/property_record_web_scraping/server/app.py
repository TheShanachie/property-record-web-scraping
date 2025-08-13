from property_record_web_scraping.server.routes import scraping_bp, init_events_handler, get_events_handler, shutdown_and_cleanup
from property_record_web_scraping.server.config_utils.Config import Config
from property_record_web_scraping.server.server_cleanup import server_cleanup
from flask import Flask
import atexit, os, signal, sys
from io import StringIO

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

def _graceful_shutdown(pid: int, app: Flask):
    """
    Handle graceful shutdown of the application.
    Does not call exit(0) to avoid double-cleanup with atexit.
    """
    # Stop Flask app and free up the port
    _stop_and_destroy_flask_app(app)
    
    # Cleanup application resources
    shutdown_and_cleanup()
    server_cleanup(pid)


def _stop_and_destroy_flask_app(app: Flask):
    """
    Fully stop and destroy the Flask app and free up the port.
    
    Args:
        app (Flask): Flask application instance to shutdown
        
    Possible errors:
        - AttributeError: If Flask app doesn't have expected attributes (_server, teardown_* funcs, blueprints, config)
        - RuntimeError: If Flask application context is already active or torn down
        - OSError: If the underlying server socket cannot be closed properly
        - Exception: General exceptions during Werkzeug server shutdown
        - KeyError: If attempting to clear config items that don't exist
        - TypeError: If Flask app object is not properly initialized
    """
    # Get the Werkzeug server if it exists
    if hasattr(app, '_server'):
        server = app._server
        if server:
            server.shutdown()
    
    # Clear handlers and config (Flask will handle context cleanup)
    app.teardown_appcontext_funcs.clear()
    app.teardown_request_funcs.clear()
    app.blueprints.clear()
    app.config.clear()


def _setup_atexit_and_signal_shutdown(pid: int, app: Flask):
    """
    Set up atexit and signal handlers for cleanup.
    This function is called during app initialization.
    
    Args:
        pid (int): Process ID of the current process, which cleanud up.
        
    Raises:
        RuntimeError: If the events handler is not initialized before this function is called.
    """
    
    # Register atexit cleanup
    atexit.register(_graceful_shutdown, pid, app)
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, lambda signum, frame: _graceful_shutdown(pid, app))
    signal.signal(signal.SIGTERM, lambda signum, frame: _graceful_shutdown(pid, app))
    

def _setup_events_handler(app: Flask):
    """
    Initialize and register the events handler.
    
    Returns:
        EventsHandler: Initialized events handler instance
    """
    
    # Initialize the events handler
    events_handler = init_events_handler(
        **Config.get_config("events_handler_init")
    )
    
    return events_handler

def _override_run_method(app):
    """
    Override the Flask app's run method to use config defaults and initialize drivers on run.
    
    Args:
        app (Flask): Flask application instance
    """
    # Store original run method
    _original_run = app.run
    
    def custom_run(host=None, port=None, debug=None, **options):
        """Override run method to use config defaults, lazy-initialize drivers, and capture CLI output"""
        
        # Capture stdout/stderr for CLI output redirection
        old_stdout, old_stderr = sys.stdout, sys.stderr
        captured_stdout_buffer = StringIO()
        captured_stderr_buffer = StringIO()
        
        try:
            # Redirect streams to capture Flask CLI output
            sys.stdout = captured_stdout_buffer
            sys.stderr = captured_stderr_buffer
            
            # Register blueprints
            _register_blueprints(app)
            
            # Setup the events handler.
            _setup_events_handler(app)
            
            # Setup the atexit shutdown
            _setup_atexit_and_signal_shutdown(os.getpid(), app)
            
            # Use config values as defaults if not provided
            host = host or app.config.get("HOST", "127.0.0.1")
            port = port or app.config.get("PORT", 5000)
            debug = debug if debug is not None else app.config.get("DEBUG", False)
            
            return _original_run(host=host, port=port, debug=debug, **options)
            
        finally:
            # Restore original streams
            sys.stdout, sys.stderr = old_stdout, old_stderr
            
            # Extract captured output
            captured_stdout = captured_stdout_buffer.getvalue()
            captured_stderr = captured_stderr_buffer.getvalue()
            
            # Close StringIO buffers to free memory
            captured_stdout_buffer.close()
            captured_stderr_buffer.close()
            
            # Note: captured output is available in captured_stdout/captured_stderr
            # variables but not processed further per user request
    
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
    
    # Override run method to use config defaults and lazy-initialize drivers
    _override_run_method(app)

    return app