import unittest, os, requests
# from test.parsing.json_schema_registry import JSONSchemaRegistry

# Add schema path to envrionemt
os.environ["API_URL"] = "http://localhost:5000/api/v1"
# os.environ["API_SCHEMA_DIR_PATH"] = os.path.join(os.path.dirname(__file__), "./test/parsing/api_schema/output")

# # Load the JSONSchemaRegistry to verify path and validate context.
# registry = JSONSchemaRegistry(directory=os.environ["API_SCHEMA_DIR_PATH"])

# Check whether the api is already running
try:
    response = requests.get(os.environ["API_URL"] + "/")
except Exception as e:
    print(f"API is not running at {os.environ['API_URL']}. Please start the API server.")
    exit(1)

# Discover and load test cases from the current directory
loader = unittest.TestLoader()
tests = loader.discover(start_dir="./test", pattern="test_*.py")  # Adjust pattern if needed

# Run the test suite
runner = unittest.TextTestRunner(verbosity=2, buffer=True, tb_locals=True)
runner.run(tests)