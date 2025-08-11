from pydantic import BaseModel
import re

def clean_str(s: str) -> str:
        """ Formal method for string cleaning. """
        # Replace '#' with number.
        s = s.replace('#', 'number')
        # Replace non-alphanumeric characters with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9]', '_', s)
        # Replace any series of _ with a single underscore
        sanitized = re.sub(r'_{2,}', '_', sanitized)
        # Strip leading and trailing underscores
        return sanitized.strip('_').lower()
    
class SanitizedBaseModel(BaseModel):
    class Config:
        alias_generator = clean_str
        validate_by_name = True