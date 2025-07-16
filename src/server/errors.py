
class TaskNotFoundError(Exception):
    """ Error for attemps to access non-existent tasks. """
    
    def __init__(self, task_id: str, message: str = None):
        self.task_id = task_id
        if not message:
            self.message = f"Error attempting to access task with id '{task_id}' which does not exist"
        else: 
            self.message = message
        super().__init__(message)
        
    def __str__(self):
        return self.message


