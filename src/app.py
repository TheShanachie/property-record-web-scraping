from flask import Flask
from server.routes import init_thread_pool, init_driver_pool, scraping_bp
import atexit
import os

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['MAX_WORKERS'] = int(os.getenv('MAX_WORKERS', 10))
    app.config['CLEANUP_INTERVAL'] = int(os.getenv('CLEANUP_INTERVAL', 1800))  # 30 minutes
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Initialize thread pool
    thread_pool = init_thread_pool(
        max_workers=app.config['MAX_WORKERS'],
        cleanup_interval=app.config['CLEANUP_INTERVAL']
    )
    print("Thread pool initialized.")
    
    # Initialize driver pool
    driver_pool = init_driver_pool(max_drivers=5)
    print("Driver pool initialized.")
    
    # Register cleanup on app shutdown
    atexit.register(lambda: thread_pool.shutdown())
    atexit.register(lambda: driver_pool.shutdown())
    
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
        debug=app.config['DEBUG'],
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        threaded=True
    )