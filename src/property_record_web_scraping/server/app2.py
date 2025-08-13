from property_record_web_scraping.server.routes import scraping_bp, init_events_handler, get_events_handler, shutdown_and_cleanup
from property_record_web_scraping.server.config_utils.Config import Config
from property_record_web_scraping.server.server_cleanup import server_cleanup
from flask import Flask
import atexit, os, signal, sys
from io import StringIO
import multiprocessing
from gunicorn.app.base import BaseApplication


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


def _graceful_shutdown(pid: int, app: Flask):
    """
    Handle graceful shutdown of the application.
    Improved shutdown that properly releases ports.
    """
    shutdown_and_cleanup()
    server_cleanup(pid)
    
    # Force exit to ensure port cleanup
    os._exit(0)


def _setup_atexit_and_signal_shutdown(pid: int, app: Flask):
    """
    Set up atexit and signal handlers for cleanup.
    
    Args:
        pid (int): Process ID of the current process
    """
    atexit.register(_graceful_shutdown, pid, app)
    signal.signal(signal.SIGINT, lambda signum, frame: _graceful_shutdown(pid, app))
    signal.signal(signal.SIGTERM, lambda signum, frame: _graceful_shutdown(pid, app))


def _setup_events_handler(app: Flask):
    """
    Initialize and register the events handler.
    
    Returns:
        EventsHandler: Initialized events handler instance
    """
    events_handler = init_events_handler(
        **Config.get_config("events_handler_init")
    )
    return events_handler


def _register_blueprints(app):
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
    workers = app.config.get("WORKERS", min(multiprocessing.cpu_count() * 2 + 1, 4))
    
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


def _run_with_dev_server(app):
    """
    Run Flask app with development server (original behavior).
    
    Args:
        app (Flask): Flask application instance
    """
    host = app.config.get("HOST", "127.0.0.1")
    port = app.config.get("PORT", 5000)
    debug = app.config.get("DEBUG", False)
    
    # Capture stdout/stderr for CLI output redirection
    old_stdout, old_stderr = sys.stdout, sys.stderr
    captured_stdout_buffer = StringIO()
    captured_stderr_buffer = StringIO()
    
    try:
        sys.stdout = captured_stdout_buffer
        sys.stderr = captured_stderr_buffer
        
        app.run(host=host, port=port, debug=debug, threaded=True, use_reloader=False)
        
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr
        captured_stdout_buffer.close()
        captured_stderr_buffer.close()


def _override_run_method_hybrid(app):
    """
    Override Flask app's run method with hybrid approach.
    Uses Gunicorn for production, dev server for debugging.
    
    Args:
        app (Flask): Flask application instance
    """
    _original_run = app.run
    
    def hybrid_run(host=None, port=None, debug=None, use_gunicorn=None, **options):
        """
        Hybrid run method supporting both Gunicorn and dev server.
        
        Args:
            use_gunicorn (bool): Force Gunicorn usage. If None, auto-detect based on debug mode.
        """
        # Setup common initialization
        _register_blueprints(app)
        _setup_events_handler(app)
        _setup_atexit_and_signal_shutdown(os.getpid(), app)
        
        # Update config with provided values
        if host:
            app.config["HOST"] = host
        if port:
            app.config["PORT"] = port
        if debug is not None:
            app.config["DEBUG"] = debug
        
        # Determine server type
        debug_mode = app.config.get("DEBUG", False)
        use_gunicorn = use_gunicorn if use_gunicorn is not None else not debug_mode
        
        if use_gunicorn and not debug_mode:
            return _run_with_gunicorn(app)
        else:
            return _run_with_dev_server(app)
    
    app.run = hybrid_run


def _create_app(use_gunicorn=None):
    """
    Create and configure the Flask application with hybrid server approach.
    
    Args:
        use_gunicorn (bool): Whether to use Gunicorn. If None, auto-detect.
        
    Returns:
        Flask: Configured Flask app instance
    """
    app = _configure_flask_app()
    
    # Check environment or config for server choice
    if use_gunicorn is None:
        use_gunicorn = app.config.get("USE_GUNICORN", True)
    
    app.config["USE_GUNICORN"] = use_gunicorn
    
    # Override run method with hybrid approach
    _override_run_method_hybrid(app)
    
    return app


def create_production_app():
    """
    Create app specifically configured for production with Gunicorn.
    
    Returns:
        Flask: Production-ready Flask app
    """
    return _create_app(use_gunicorn=True)


def create_dev_app():
    """
    Create app specifically configured for development server.
    
    Returns:
        Flask: Development Flask app
    """
    return _create_app(use_gunicorn=False)