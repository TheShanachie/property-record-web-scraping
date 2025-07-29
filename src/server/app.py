from server.routes import scraping_bp, init_events_handler
from server.config_utils.Config import Config
from flask import Flask
import atexit, os

def _create_app():
    """
        Create and configure the Flask application. Return a ready-to-use Flask app instance.
        This function is intented to be called in the server module __init.py file. There are 
        a number of relative dependencies that need to be resolved before the app can be created.        
    """    
    
    # Initialize the events handler for our application.
    events_handler = init_events_handler(
        **Config.get_config('events_handler_init')  # Load events handler configuration from the config
    )
    
    # Create the Flask app instance
    app = Flask(__name__)
    
    # Register cleanup on app shutdown
    atexit.register(lambda: events_handler.shutdown())
    
    # Register blueprints
    app.register_blueprint(scraping_bp, url_prefix='/api/v1')
    
    # Return the build Flask app.
    return app
    
    