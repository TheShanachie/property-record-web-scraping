from property_record_web_scraping.server.routes import scraping_bp, init_events_handler, shutdown_and_cleanup
from property_record_web_scraping.server.config_utils.Config import Config
from property_record_web_scraping.server.server_cleanup import server_cleanup
from flask import Flask
import atexit, os, signal
from gunicorn.app.base import BaseApplication

# Global flag to prevent multiple atexit handler registrations
_cleanup_registered = False


class GunicornApp(BaseApplication):
    """
    Custom Gunicorn application class for embedding Gunicorn server.
    """
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        """Load Gunicorn configuration from options"""
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)

    def load(self):
        """Return the Flask application"""
        return self.application


def _configure_flask_app():
    """
    Configure and create the Flask application instance.
    
    Returns:
        Flask: Configured Flask app instance
    """
    flask_config = Config.get_config("flask_app")
    host = flask_config.get("HOST", "127.0.0.1")
    port = flask_config.get("PORT", 5000)

    app = Flask(__name__)
    app.config.update(flask_config)
    app.config["BASE_URL"] = f"http://{host}:{port}"
    
    return app


def _graceful_shutdown(pid: int):
    """
    Handle graceful shutdown of the application.
    Improved shutdown that properly releases ports.
    """
    try:
        shutdown_and_cleanup()
    except Exception as e:
        print(f"Warning: Error during shutdown_and_cleanup: {e}")
    
    try:
        server_cleanup(pid)
    except Exception as e:
        print(f"Warning: Error during server_cleanup: {e}")
    
    # Let process exit naturally after cleanup completes


def _setup_atexit_and_signal_shutdown(pid: int):
    """
    Set up atexit and signal handlers for cleanup.
    Only registers handlers once to prevent multiple cleanup attempts.
    
    Args:
        pid (int): Process ID of the current process
    """
    global _cleanup_registered
    if not _cleanup_registered:
        atexit.register(_graceful_shutdown, pid)
        signal.signal(signal.SIGINT, lambda _signum, _frame: _graceful_shutdown(pid))
        signal.signal(signal.SIGTERM, lambda _signum, _frame: _graceful_shutdown(pid))
        _cleanup_registered = True


def _setup_events_handler():
    """
    Initialize and register the events handler.
    
    Returns:
        EventsHandler: Initialized events handler instance
    """
    events_handler = init_events_handler(
        **Config.get_config("events_handler_init")
    )
    return events_handler


def _register_blueprints(app: Flask):
    """
    Register all application blueprints.
    
    Args:
        app (Flask): Flask application instance
    """
    app.register_blueprint(scraping_bp, url_prefix='/api/v1')


def _run_with_gunicorn(app):
    """
    Run Flask app with embedded Gunicorn server for better port management.
    
    Args:
        app (Flask): Flask application instance
    """
    host = app.config.get("HOST", "127.0.0.1")
    port = app.config.get("PORT", 5000)
    workers = app.config.get("WORKERS", 1)  # Use single worker due to internal threading
    
    options = {
        'bind': f'{host}:{port}',
        'workers': workers,
        'worker_class': 'sync',
        'timeout': 30,
        'graceful_timeout': 10,
        'max_requests': 1000,
        'max_requests_jitter': 100,
        'preload_app': True,
        'reuse_port': True,
        'worker_tmp_dir': '/dev/shm',
        'keepalive': 5
    }
    
    GunicornApp(app, options).run()


def _override_run_method(app):
    """
    Override the Flask app's run method to always use Gunicorn.
    
    Args:
        app (Flask): Flask application instance
    """
    def gunicorn_run(host=None, port=None, debug=None, **_options):
        """
        Override run method to always use Gunicorn for better port management.
        """
        # Setup initialization
        _register_blueprints(app)
        _setup_events_handler()
        _setup_atexit_and_signal_shutdown(os.getpid())
        
        # Update config with provided values
        if host:
            app.config["HOST"] = host
        if port:
            app.config["PORT"] = port
        if debug is not None:
            app.config["DEBUG"] = debug
        
        # Always use Gunicorn
        return _run_with_gunicorn(app)
    
    app.run = gunicorn_run


def _create_app():
    """
    Create and configure the Flask application with Gunicorn.
    
    Returns:
        Flask: Configured Flask app instance
    """
    app = _configure_flask_app()
    
    # Override run method to use Gunicorn
    _override_run_method(app)
    
    return app