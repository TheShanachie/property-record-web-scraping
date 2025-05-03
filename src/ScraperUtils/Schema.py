from jsonschema import validate
from jsonschema.exceptions import ValidationError, SchemaError

def validate_search_schema(args: dict):
    """
    Validate search arguments.

    Args:
        args (dict): The search arguments

    Returns:
        bool: True if the search arguments are valid
    """

    # Define the schema for search arguments
    search_schema = {
        "type": "object",
        "properties": {
            "building_style": {"type": "string"},
            "municipality": {"type": "string"},
            "neighborhood": {"type": "string"},
            "number_of_stories": {
                "type": "object",
                "properties": {"to": {"type": "integer"}, "from": {"type": "integer"}},
                "required": ["to", "from"],
            },
            "sale_amount": {
                "type": "object",
                "properties": {"to": {"type": "integer"}, "from": {"type": "integer"}},
                "required": ["to", "from"],
            },
            "sales_date": {
                "type": "object",
                "properties": {"to": {"type": "string"}, "from": {"type": "string"}},
                "required": ["to", "from"],
            },
            "school_district": {"type": "string"},
            "square_feet": {
                "type": "object",
                "properties": {"to": {"type": "integer"}, "from": {"type": "integer"}},
                "required": ["to", "from"],
            },
            "street": {"type": "string"},
            "year_built": {
                "type": "object",
                "properties": {"to": {"type": "string"}, "from": {"type": "string"}},
                "required": ["to", "from"],
            },
        },
        "required": [
            "building_style",
            "municipality",
            "neighborhood",
            "number_of_stories",
            "sale_amount",
            "sales_date",
            "school_district",
            "square_feet",
            "street",
            "year_built",
        ],
        "additionalProperties": False,
    }
    
    try:
        # Validate the search arguments
        validate(instance=args, schema=search_schema)
        return True

    # The search arguments are invalid
    except ValidationError as e:
        return False
        
    # The actual schema is invalid
    except SchemaError as e:
        return False