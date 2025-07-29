from flask import Blueprint, jsonify, request
from typing import Callable, Tuple, Any, Dict, Optional, List
from pydantic import ValidationError
from server.events import EventsHandler
from server.models import ActionInput, ActionOutput
import time, json, uuid, traceback
from functools import wraps
from server.logging_utils.loggers import flask_app_interactions_logger

# Create a Blueprint instead of Flask app
scraping_bp = Blueprint('scraping', __name__)


def init_events_handler(max_drivers: int = 5, max_workers: int = 5, cleanup_interval: int = 3600):
    """Initialize the EventsHandler - call from main app"""
    global events_handler
    events_handler = EventsHandler(max_drivers=max_drivers, 
                                   max_workers=max_workers, 
                                   cleanup_interval=cleanup_interval)
    return events_handler

def get_events_handler():
    """Get the current EventsHandler instance"""
    global events_handler
    if events_handler is None:
        raise RuntimeError(
            "EventsHandler not initialized. Call init_events_handler() first.")
    return events_handler


def log_flask_endpoint_io(logger):
    """
    Decorator to log input request and output response of a Flask endpoint.
    
    Args:
        logger (logging.Logger): Configured logger instance from your utility.
    
    Returns:
        function: Wrapped endpoint function with logging.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Log incoming request
                logger.info(f"Incoming {request.method} request to {request.path}")
                logger.debug(f"Request Headers: {dict(request.headers)}")
                
                # Is there any data associated with the request?
                if request.data:
                    logger.debug(f"Request Data: {request.data.decode('utf-8', errors='ignore')}")

                # if request.is_json:
                #     logger.debug(f"Request JSON: {json.dumps(request.get_json(force=True), indent=2)}")
                # else:
                #     logger.debug(f"Request Data: {request.data.decode('utf-8', errors='ignore')}")

            except Exception as e:
                logger.warning(f"Failed to log incoming request: {e}", exc_info=True)

            response = func(*args, **kwargs)

            try:
                # Log outgoing response
                logger.info(f"Outgoing response for {request.method}: {response}")
                if hasattr(response, "get_data"):
                    logger.debug(f"Response Data: {response.get_data(as_text=True)}")
            except Exception as e:
                logger.warning(f"Failed to log outgoing response: {e}", exc_info=True)

            return response
        return wrapper
    return decorator


@scraping_bp.route('/scrape', methods=['POST'])
@log_flask_endpoint_io(flask_app_interactions_logger)
def scrape():
    """
        This function handles the submission of a scraping task. It validates the input data, extracts the necessary parameters, and posts the task to the TaskManager. If successful, it returns the metadata of the task. If there is a validation error, it returns a 400 status code with the error message. If there is any other error, it returns a 500 status code with the error message

        :return: JSON response containing the task metadata and error data
        :rtype: tuple[str, int]
    """
    try:
        handler = get_events_handler()
        ActionInput.Scrape.model_validate(request.json)  # Validate the input data
        data = ActionInput.Scrape(**request.json)
        ActionInput.Scrape.model_validate(data)  # Validate the input data
        result = handler.scrape(data)
        return result.json_dump()

    except ValidationError as ve:
    
        # There was some validation error in the input data
        result = ActionOutput.OutputModel(
            error=ve,
            status_code=400, # Bad Request
        )
        return result.json_dump()

    except Exception as e:
        
        # Some other error occurred
        result = ActionOutput.OutputModel(
            error=e,
            status_code=500, # Internal Server Error
        )
        return result.json_dump()


@scraping_bp.route('/task/<task_id>/status', methods=['GET'])
@log_flask_endpoint_io(flask_app_interactions_logger)
def status(task_id):
    """
        This function retrieves the status of a specific task by its ID. It uses the EventsHandler to get the current status of the task and returns it as a JSON response. This function returns all available metadata for a test, regardless of the status.
    
        :param task_id: The ID of the task to retrieve the status for
        :type task_id: str
        :return: JSON response containing the task status and error data
        :rtype: tuple[str, int]
    """
    try: 
        # Get the EventsHandler instance
        handler = get_events_handler()

        # Retrieve the task status from the TaskManager
        status = handler.status(ActionInput.Status(task_id=task_id))
        
        # Return the status as a JSON response
        return status.json_dump()

    except Exception as e:
        
        # Handle any exceptions that occur
        result = ActionOutput.OutputModel(
            error=e,
            status_code=500, # Internal Server Error
        )
        return result.json_dump()


@scraping_bp.route('/task/<task_id>/result', methods=['GET'])
@log_flask_endpoint_io(flask_app_interactions_logger)
def result(task_id):
    """
        This function retrieves the result of a specific task by its ID. It uses the EventsHandler to get the result of the task and returns it as a JSON response. If the task is still running, it will return an empty result.
    
        :param task_id: The ID of the task to retrieve the result for
        :type task_id: str
        :return: JSON response containing the task result and error data
        :rtype: tuple[str, int]
    """
    try:
        # Get the EventsHandler instance
        handler = get_events_handler()

        # Retrieve the task result from the TaskManager
        result = handler.result(ActionInput.Result(task_id=task_id))

        # Return the result as a JSON response
        return result.json_dump()

    except Exception as e:
        
        # Handle any exceptions that occur
        result = ActionOutput.OutputModel(
            error=e,
            status_code=500, # Internal Server Error
        )
        return result.json_dump()


@scraping_bp.route('/task/<task_id>/wait', methods=['GET'])
@log_flask_endpoint_io(flask_app_interactions_logger)
def wait(task_id):
    """
        This function waits for a specific task to complete by its ID. It uses the EventsHandler to wait for the task to finish and returns the result as a JSON response. If the task is still running, it will block until the task is completed. The function currently does not accept a timeout argument, but is set to wait 60 seconds via the default behavior of the EventsHandler.
    
        :param task_id: The ID of the task to wait for
        :type task_id: str
        :return: JSON response containing the task result and error data
        :rtype: tuple[str, int]
    """
    
    try:
        # Get the EventsHandler instance
        handler = get_events_handler()

        # Wait for the task to complete
        result = handler.wait(ActionInput.Wait(task_id=task_id))

        # Return the result as a JSON response
        return result.json_dump()

    except Exception as e:
        
        # Handle any exceptions that occur
        result = ActionOutput.OutputModel(
            error=e,
            status_code=500, # Internal Server Error
        )
        return result.json_dump()


@scraping_bp.route('/task/<task_id>/cancel', methods=['POST'])
@log_flask_endpoint_io(flask_app_interactions_logger)
def cancel(task_id):
    """ 
        This function is currently not implemented. It is a placeholder for future functionality. 
    
        :param task_id: The ID of the task to cancel
        :type task_id: str
        :return: JSON response indicating that the function is not implemented
        :rtype: tuple[str, int]    
    """
    
    result = ActionOutput.OutputModel(
        status_code=501,  # Not Implemented
    )
    return result.json_dump()


@scraping_bp.route('/tasks', methods=['GET'])
@log_flask_endpoint_io(flask_app_interactions_logger)
def tasks():
    """
        This function retrieves all tasks from the TaskManager. It uses the EventsHandler to get the list of all tasks and returns them as a JSON response.
        
        :return: JSON response containing all tasks and error data
        :rtype: tuple[str, int]
    """
    try:
        # Get the EventsHandler instance
        handler = get_events_handler()

        # Retrieve all tasks from the TaskManager
        tasks = handler.get_all_tasks()

        # Return the tasks as a JSON response
        return tasks.json_dump()

    except Exception as e:

        # Handle any exceptions that occur
        result = ActionOutput.OutputModel(
            error=e,
            status_code=500, # Internal Server Error
        )
        return result.json_dump()


@scraping_bp.route('/health', methods=['GET'])
@log_flask_endpoint_io(flask_app_interactions_logger)
def health():
    """
        This function performs a health check on the TaskManager. It uses the EventsHandler to check the health status and returns it as a JSON response.
        
        :return: JSON response containing the health status and error data
        :rtype: tuple[str, int]
    """
    
    try:
        # Get the EventsHandler instance
        handler = get_events_handler()

        # Perform a health check on the TaskManager
        health_status = handler.health()

        # Return the health status as a JSON response
        return health_status.json_dump()

    except Exception as e:
        
        # Handle any exceptions that occur
        result = ActionOutput.OutputModel(
            error=e,
            status_code=500,  # Internal Server Error
        )
        return result.json_dump()
