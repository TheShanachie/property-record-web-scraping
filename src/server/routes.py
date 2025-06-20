from flask import Blueprint, jsonify, request
from typing import Callable, Tuple, Any, Dict, Optional, List
from .thread_pool_manager import WebScrapingThreadPool, TaskData
from .driver_pool import DriverPool
import time, uuid, traceback
from dataclass import dataclass, field

# Create a dataclass for the Response structure
@dataclass
class Response:
    pass

# Create a Blueprint instead of Flask app
scraping_bp = Blueprint('scraping', __name__)

def init_thread_pool(max_workers=10, cleanup_interval=1800):
    """Initialize the thread pool - call from main app"""
    global thread_pool
    thread_pool = WebScrapingThreadPool(max_workers=max_workers, cleanup_interval=cleanup_interval)
    return thread_pool


def get_thread_pool():
    """Get the current thread pool instance"""
    global thread_pool
    if thread_pool is None:
        raise RuntimeError("Thread pool not initialized. Call init_thread_pool() first.")
    return thread_pool


def init_driver_pool(max_drivers=5):
    """Initialize the driver pool - call from main app."""
    global driver_pool
    driver_pool = DriverPool(max_drivers=5)
    return driver_pool


def get_driver_pool():
    """Get the current driver pool"""
    global driver_pool
    if driver_pool is None:
        raise RuntimeError("Driver pool is not initialized. Call init_driver_pool() first.")
    return driver_pool


def scrape_address(address: tuple, pages: list, num_results: int): # This is our worker function...
    """Worker function to scrape address from property site.""" 
    driver_pool = get_driver_pool() # Assumes driver pool is initialized.
    driver = driver_pool.acquire_driver()
    results = driver.address_search(address, pages, num_results)
    driver.reset() # Currently, we clean up the driver before returning. This behavior needs to change eventually.
    driver_pool.release_driver(driver=driver)
    return results

def create_json_response(task_result: Optional[Dict[str, Any]], status_code: int = 200):
    """Helper function to create JSON responses for Flask"""
    if task_result is None:
        return {"error": "Task not found"}, 404
    return task_result, status_code


@scraping_bp.route('/scrape', methods=['POST'])
def submit_scraping_task():
    """
    Submit a web scraping task using the driver pool.
    Expected JSON payload:
    {
        "address": [123, "Main St", "E"],
        "pages": ["..."],
        "max_results": 50
    }
    """
    try:
        # Get the request data.
        data = request.get_json()
        print(data)
        
        if len(data.keys()) != 3:
            return jsonify({"error": "Invalid number of fields. Expected 3 fields: 'address', 'pages', and 'max_results'."}), 400
        
        # Require three data points, address, pages, and max-results.
        if not all(['address' in data,
                    'pages' in data,
                    'max_results' in data]):
            return jsonify({"error": "Misssing one of required fields. Expected 'address', 'pages', and 'max_results'. Example: {'address': [123, 'Main St', 'E'], 'pages: ['...''], 'max_results': 50}"}), 400

        address = data['address']
        if not isinstance(address, list) or len(address) != 3:
            return jsonify({"error": "Address must be a list of [int, str, str]"}), 400
        if not isinstance(address[0], int) or not isinstance(address[1], str) or not isinstance(address[2], str):
            return jsonify({"error": "Address format must be [int, str, str]"}), 400

        pages = data['pages']
        if not isinstance(pages, list) or not all(isinstance(page, str) for page in pages):
            return jsonify({"error": "Pages must be a list of strings"}), 400

        possible_pages = ["Parcel", "Owner", "Multi-Owner", "Residential", "Land", "Values", "Homestead", "Sales"]
        for page in pages:
            if page not in possible_pages:
                return jsonify({"error": f"Invalid page name: {page}"}), 400

        max_results = data['max_results']
        if not isinstance(max_results, int) or max_results <= 0:
            return jsonify({"error": "max_results must be a positive integer"}), 400
        if max_results > 10:
            max_results = 10
            
            
        # Get the thread pool and submit the task
        thread_pool = get_thread_pool()
        search_data = {'address': tuple(address),
                       'pages': pages,
                       'num_results': max_results
                       }
        task_data = thread_pool.submit_task(func=scrape_address,
                                            kwargs=search_data)
        return create_json_response(task_result=task_data.to_dict(),
                                    status_code=202)

    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@scraping_bp.route('/task/<task_id>/status', methods=['GET'])
def get_task_status(task_id):
    """Get the current status of a task"""
    task_result = get_thread_pool().get_task_status(task_id)
    return create_json_response(task_result.to_dict())


@scraping_bp.route('/task/<task_id>/result', methods=['GET'])
def get_task_result(task_id):
    """Get the result of a completed task"""
    task_result = get_thread_pool().get_task_status(task_id)
    
    if not task_result:
        return jsonify({"error": "Task not found"}), 404
    
    status = task_result.status
    if status == 'completed':
        return create_json_response(task_result=task_result.to_dict(), status_code=200)
    elif status == 'error':
        return create_json_response(task_result=task_result.to_dict(), status_code=500)
    else:
        return create_json_response(task_result=task_result.to_dict(), status_code=202)


@scraping_bp.route('/task/<task_id>/wait', methods=['GET'])
def wait_for_task(task_id):
    """Wait for a task to complete (with optional timeout)"""
    timeout = request.args.get('timeout', type=int)  # Optional timeout in seconds
    
    task_result = get_thread_pool().wait_for_task(task_id, timeout=timeout)
    
    if not task_result:
        return jsonify({"error": "Task not found or timeout exceeded"}), 404

    return create_json_response(task_result=task_result.to_dict())


@scraping_bp.route('/task/<task_id>/cancel', methods=['POST'])
def cancel_task(task_id):
    """Cancel a pending task"""
    cancelled = get_thread_pool().cancel_task(task_id)
    
    if cancelled:
        return jsonify({
            "task_id": task_id,
            "status": "cancelled",
            "message": "Task cancelled successfully"
        })
    else:
        return jsonify({
            "task_id": task_id,
            "status": "not_cancelled",
            "message": "Task could not be cancelled (may already be running or completed)"
        }), 400


@scraping_bp.route('/tasks', methods=['GET'])
def get_all_tasks():
    """Get status of all tasks"""
    active_only = request.args.get('active_only', '').lower() == 'true'
    
    if active_only:
        tasks = get_thread_pool().get_active_tasks()
    else:
        tasks = get_thread_pool().get_all_tasks()
    
    return jsonify({
        "tasks": tasks,
        "count": len(tasks)
    })


@scraping_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        pool = get_thread_pool()
        active_tasks = pool.get_active_tasks()
        
        return jsonify({
            "status": "healthy",
            "thread_pool": "active",
            "active_tasks": len(active_tasks),
            "timestamp": time.time()
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }), 500