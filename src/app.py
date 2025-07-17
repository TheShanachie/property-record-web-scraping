from flask import Flask
from server.routes import init_events_handler, scraping_bp
import atexit, os

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['MAX_DRIVERS'] = int(os.getenv('MAX_DRIVERS', 1))
    app.config['MAX_WORKERS'] = int(os.getenv('MAX_WORKERS', 5))
    app.config['CLEANUP_INTERVAL'] = int(os.getenv('CLEANUP_INTERVAL', 3600))
    
    # Initialize events handler.
    events_handler = init_events_handler(
        max_drivers=app.config['MAX_DRIVERS'],
        max_workers=app.config['MAX_WORKERS'],
        cleanup_interval=app.config['CLEANUP_INTERVAL']
    )
    
    # Register cleanup on app shutdown
    atexit.register(lambda: events_handler.shutdown())
    
    # Register blueprints
    app.register_blueprint(scraping_bp, url_prefix='/api/v1')
    
    # Add some basic routes
    @app.route('/')
    def index():
        return {
            "message": "Web Scraping API",
            "version": "1.0",
            "endpoints": {
                "submit_task": "POST /api/v1/scrape",
                "task_status": "GET /api/v1/task/<task_id>/status",
                "task_result": "GET /api/v1/task/<task_id>/result",
                "wait_for_task": "GET /api/v1/task/<task_id>/wait",
                "cancel_task": "POST /api/v1/task/<task_id>/cancel",
                "all_tasks": "GET /api/v1/tasks",
                "health_check": "GET /api/v1/health"
            }
        }
    
    @app.route('/health')
    def health():
        return {"status": "healthy", "app": "running"}
    
    return app

# Create the Flask app
app = create_app()

if __name__ == '__main__':
    app.run(
        debug=False,
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        threaded=True
    )