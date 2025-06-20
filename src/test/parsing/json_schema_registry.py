import os
import json
import referencing
from jsonschema import Draft202012Validator

class JSONSchemaRegistry:
    def __init__(self, directory: str):
        """Initialize the registry and populate it with JSON schemas."""
        self.directory = directory
        
        # Create and load the referencing registry
        self.registry = referencing.Registry()
        self._load_schemas(directory)
        
        # Check references in the loaded schemas
        self.validate_schema_references()
        
        # Create an object for holding validators
        self.validators = {}
        
    def _load_schemas(self, directory: str):
        """Recursively load JSON schemas and register them with referencing."""
        # Load schemas into the registry
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r") as f:
                        schema_data = json.load(f)
                        schema_id = schema_data.get("$id", file_path)
                        resource = referencing.Resource.from_contents(schema_data)
                        self.registry = self.registry.with_resource(uri=f"{schema_id}", resource=resource)

    def get_schema(self, schema_name: str):
        """Retrieve a JSON schema by name or path, handling missing references gracefully."""
        try:
            return self.registry.get(schema_name)
        except referencing.exceptions.Unresolvable:
            raise ValueError(f"Schema '{schema_name}' not found in the registry.")
        
    def has_schema(self, schema_name: str) -> bool:
        """Check if a schema exists in the registry."""
        return schema_name in self.list_schemas()

    def list_schemas(self):
        """List all registered schema names."""
        return list(self.registry.keys())
    
    def get_validator(self, schema: str) -> Draft202012Validator:
        """Build/Get the JSON schema validator after checking registry existence."""
        if schema not in self.list_schemas():  # Use explicit listing
            raise ValueError(f"Schema '{schema}' not found in registry.")
        if schema not in self.validators:
            schema_data = self.registry.get(schema).contents
            self.validators[schema] = Draft202012Validator(schema_data, registry=self.registry)
        return self.validators[schema]
    
    def validate(self, schema: str, data: dict):
        """Validate data against a specified schema."""
        validator = self.get_validator(schema)
        errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
        if errors:
            raise ValueError(f"Validation errors for schema '{schema}': {errors}")
        return True
    
    def validate_schema_references(self):
        """Ensure all $ref paths in registered schemas exist in the registry."""
        missing_refs = []

        for schema_name in self.list_schemas():
            schema_data = self.registry.get(schema_name).contents

            # Recursively check for $ref in schema
            def check_refs(sub_schema, path="root"):
                if isinstance(sub_schema, dict):
                    if "$ref" in sub_schema:
                        ref_path = sub_schema["$ref"]
                        if not self.has_schema(ref_path):  # Check if reference exists
                            missing_refs.append((path, ref_path))
                    for key, value in sub_schema.items():
                        check_refs(value, f"{path}.{key}")
                elif isinstance(sub_schema, list):
                    for index, item in enumerate(sub_schema):
                        check_refs(item, f"{path}[{index}]")

            check_refs(schema_data)

        if missing_refs:
            raise ValueError(f"Missing $ref references: {missing_refs}")

        return True  # No missing references
    
        
        