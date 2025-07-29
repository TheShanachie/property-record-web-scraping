from typing import Tuple, Optional, Type
from pydantic import BaseModel, ValidationError
from server.models import ActionInput, ActionOutput
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
        
    
    def submit_scrape_job(self, scrape_input: ActionInput.Scrape, validate_input: bool = False) -> ActionOutput.OutputModel:
        """ Submit scrape job with input validation. Do not raise an error if the input validation fails, instead assert the response status code is in the 400s. """
    
        # Validate input model
        if validate_input:
            validated_input = ActionInput.Scrape.model_validate(scrape_input.model_dump())

        # Make request
        response_data, status_code = self._make_request(
            'POST', 
            '/scrape', 
            validated_input.model_dump()
        )
        
        # Create and validate output model
        output = ActionOutput.OutputModel(
            metadata=response_data.get('metadata'),
            error=response_data.get('error'),
            status_code=status_code
        )
        
        return output
    
    def get_task_status(self, task_id: str) -> ActionOutput.OutputModel:
        """Get task status with validation"""
        
        # Validate input
        status_input = ActionInput.Status(task_id=task_id)
        
        # Make request
        response_data, status_code = self._make_request(
            'GET', 
            f'/task/{task_id}/status'
        )
        
        # Create and validate output model
        output = ActionOutput.OutputModel(
            metadata=response_data.get('metadata'),
            error=response_data.get('error'),
            status_code=status_code
        )
        
        return output
    
    def get_health(self) -> ActionOutput.OutputModel:
        """Get health status with validation"""
        response_data, status_code = self._make_request('GET', '/health')
        
        # Create and validate output model
        output = ActionOutput.OutputModel(
            metadata=response_data.get('metadata'),
            error=response_data.get('error'),
            status_code=status_code
        )
        
        return output
    
    def get_task_result(self, task_id: str) -> ActionOutput.OutputModel:
        """Get task result with validation"""
        result_input = ActionInput.Result(task_id=task_id)
        
        response_data, status_code = self._make_request(
            'GET', 
            f'/task/{task_id}/result'
        )
        
        output = ActionOutput.OutputModel(
            metadata=response_data.get('metadata'),
            error=response_data.get('error'),
            status_code=status_code
        )
        
        return output
    
    def wait_for_task(self, task_id: str) -> ActionOutput.OutputModel:
        """Wait for task completion with validation"""
        wait_input = ActionInput.Wait(task_id=task_id)
        
        response_data, status_code = self._make_request(
            'GET', 
            f'/task/{task_id}/wait'
        )
        
        output = ActionOutput.OutputModel(
            metadata=response_data.get('metadata'),
            error=response_data.get('error'),
            status_code=status_code
        )
        
        return output