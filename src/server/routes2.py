from flask import Blueprint, jsonify, request
from typing import Callable, Tuple, Any, Dict, Optional, List
from .events import EventsHandler
from models import ActionInput, ActionOutput, TaskStatus, TaskResult
import time, uuid, traceback

# Create a Blueprint instead of Flask app
scraping_bp = Blueprint('scraping', __name__)

def init_events_handler():
    """Initialize the EventsHandler - call from main app"""
    global events_handler
    events_handler = EventsHandler()
    return events_handler

def get_events_handler():
    """Get the current EventsHandler instance"""
    global events_handler
    if events_handler is None:
        raise RuntimeError("EventsHandler not initialized. Call init_events_handler() first.")
    return events_handler


@scraping_bp.route('/scrape', methods=['POST'])
def submit_scraping_task():
    """"""
    try:
        handler = get_events_handler()
        data = ActionInput.Scrape(**request.json)
        result = handler.scrape(data)
        return result.json_dump()
        
    except Exception as e:
        
        result = ActionOutput.OutputModel(
            error=str(e),
            status_code=400,
        return jsonify({"error": str(e)}), 400  


@scraping_bp.route('/task/<task_id>/status', methods=['GET'])
def get_task_status(task_id):
    """"""
    pass


@scraping_bp.route('/task/<task_id>/result', methods=['GET'])
def get_task_result(task_id):
    """"""
    pass


@scraping_bp.route('/task/<task_id>/wait', methods=['GET'])
def wait_for_task(task_id):
    """"""
    pass


@scraping_bp.route('/task/<task_id>/cancel', methods=['POST'])
def cancel_task(task_id):
    """ This function is currently not implemented. It is a placeholder for future functionality. """
    pass


@scraping_bp.route('/tasks', methods=['GET'])
def get_all_tasks():
    """"""
    try:
        # Get the EventsHandler instance
        handler = get_events_handler()
        
        # Retrieve all tasks from the TaskManager
        tasks = handler.tasks()
        
        # TODO: How should we handle the response? 
        # TODO: Create some gereric response model to exand on.
        return

    except:
        
        # TODO: How do we handle errors?
        return


@scraping_bp.route('/health', methods=['GET'])
def health_check():
    """"""
    pass