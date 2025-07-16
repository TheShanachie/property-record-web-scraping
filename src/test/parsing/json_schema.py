import json
from jsonschema import validate
from pathlib import Path
from typing import Dict

    
class JSONValidation:
    def __init__(self, schema: Dict | Path):
        """Initialize the cleaner with the given JSON schema."""
        if isinstance(schema, Dict):
            self.schema = schema
        elif isinstance(schema, Path):
            with open(schema, 'r') as file:
                self.schema = json.load(file)
        else: 
            raise TypeError("Arg: schema must be Dictionary or pathlib.Path")

    def clean(self, data, schema=None):
        """Recursively remove properties not present in the JSON schema."""
        schema = self.schema
        if isinstance(data, dict):
            allowed_keys = schema.get("properties", {})
            cleaned_data = {}

            for key, value in data.items():
                if key in allowed_keys:
                    sub_schema = allowed_keys[key]
                    if isinstance(sub_schema, dict) and "properties" in sub_schema:
                        cleaned_data[key] = self.clean(value, sub_schema)
                    else:
                        cleaned_data[key] = value

            return cleaned_data

        elif isinstance(data, list):
            return [self.clean(item, schema) for item in data]

        else:
            return data
        
    def clean_validation(self, data: dict):
        """
        First clean the icoming object then attemp to validate. This method cointains no 
        error handling, hoping to expose errors raised from the jsconschema validation.
        """
        # First clean the data.
        cleaned_data = self.clean(data)
        
        # Then validate the cleaned data against the schema.
        validate(instance=cleaned_data, schema=self.schema)
        
        
    def basic_validation(self, data: dict):
        """
        Use basic JSON schema validations without pruning the original data. Expose
        any errors raised from the JSON Schema.
        """
        
        # Then validate the cleaned data against the schema.
        validate(instance=data, schema=self.schema)
        
    