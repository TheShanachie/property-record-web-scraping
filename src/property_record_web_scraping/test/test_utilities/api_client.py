from typing import Tuple, Optional, Type
from pydantic import BaseModel, ValidationError
from server.models import ActionInput, ActionOutput
from .logger import test_logger
import requests
import json

class APIClient:
    """Enhanced API client with Pydantic model validation"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
    
    def _make_request(self, method: str, endpoint: str, data: Optional[dict] = None) -> Tuple[dict, int]:
        """Make HTTP request and return (response_dict, status_code)"""
        url = f"{self.base_url}{endpoint}"
        
        if method.upper() == 'POST':
            response = requests.post(url, json=data, timeout=30)
        elif method.upper() == 'GET':
            response = requests.get(url, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        test_logger.debug(f"Made API request with url: {url} and data: {json.dumps(data, indent=2) if data is not None else ''} response: {json.dumps(response.json(), indent=2)}")

        try:
            response_data = response.json()
        except:
            response_data = {"error": "Invalid JSON response"}
        
        return response_data, response.status_code
    
    def active_base_url(self) -> bool:
        """Check if the base URL is active by making a health check request"""
        try:
            response_data, status_code = self._make_request('GET', '/health')
            return status_code == 200 and 'health' in response_data and response_data['health'] == 'healthy'
        except requests.RequestException:
            return False
    
    def model_is_valid(self, model: Type[BaseModel], data: dict) -> bool:
        """Check if data is valid for the given Pydantic model"""
        try:
            model.model_validate(data)
            return True
        except ValidationError:
            return False
        
    
    def submit_scrape_job(self, scrape_input: dict) -> ActionOutput.Scrape:
        """ Submit scrape job with input validation. Do not raise an error if the input validation fails, instead assert the response status code is in the 400s. """
            
        # Make request
        response, _ = self._make_request(
            method='POST', 
            endpoint='/scrape', 
            data=scrape_input
        )
        test_logger.debug(f"Submitted scrape job with data: {json.dumps(scrape_input, indent=2)} - response: {json.dumps(response, indent=2)}")
        return ActionOutput.Scrape.model_validate(response)
    
    
    def get_task_status(self, task_id: str) -> ActionOutput.Status:
        """Get task status with validation"""
        response, _ = self._make_request(
            'GET', 
            f'/task/{task_id}/status'
        )
        test_logger.debug(f"Got task status for task {task_id} - response: {json.dumps(response, indent=2)}")
        return ActionOutput.Status.model_validate(response)
    
    
    def get_health(self) -> ActionOutput.Health:
        """Get health status with validation"""
        response_data, _ = self._make_request('GET', '/health')
        return ActionOutput.Health.model_validate(response_data)
    
    
    def get_tasks(self) -> ActionOutput.Tasks:
        """Get list of tasks with validation"""
        response_data, _ = self._make_request('GET', '/tasks')
        return ActionOutput.Tasks.model_validate(response_data)
    
    
    def get_task_result(self, task_id: str) -> ActionOutput.Result:
        """Get task result with validation"""
        
        response, _ = self._make_request(
            'GET', 
            f'/task/{task_id}/result'
        )
        test_logger.debug(f"Getting task result for ID: {task_id} - response: {json.dumps(response, indent=2)}")
        return ActionOutput.Result.model_validate(response)