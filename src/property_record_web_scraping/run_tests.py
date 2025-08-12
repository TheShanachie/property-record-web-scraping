import unittest, os, requests, time, sys, signal

# Use centralized Config for path setup
from property_record_web_scraping.server.config_utils import Config
Config.setup_python_path()
import property_record_web_scraping.server as server

# Set up project root using centralized Config
PROJECT_ROOT = Config.get_project_root()
os.environ["PROJECT_ROOT"] = str(PROJECT_ROOT)
os.environ["API_URL"] = "http://localhost:5000/api/v1"

server_app_id = None

# Assert basic consditions about the start state.
def assert_start_conditions():
    """
    Assert basic conditions about the start state.
    """
    # This port 5000 is not in use.
    assert not os.system("lsof -i :5000") == 0, "Port 5000 is already in use. Please stop the server before running tests."

# Start the server with an id to close it later.
def start_server():
    """
    Start the server process in the background, returning an identifier for the process to be closes later.
    """
    global server_app_id
    if server_app_id is not None:
        return server_app_id

    # Start the server
    server_app_id = os.fork()
    if server_app_id == 0:  # Child process
        app_path = os.path.join(PROJECT_ROOT, "src", "property_record_web_scraping", "app.py")
        os.execv(sys.executable, [sys.executable, app_path])
    else:  # Parent process
        return server_app_id
    
    
def stop_server():
    """
    Stop the server process using the identifier.
    """
    global server_app_id
    if server_app_id is None:
        print("No server is running.")
        return

    try:
        os.kill(server_app_id, signal.SIGKILL)  # Send SIGKILL to forcefully stop the server
    except OSError as e:
        print(f"Error stopping server: {e}")
    finally:
        server_app_id = None

# Define some basic helpers
def wait_server(interval: int = 10, timeout: int = 60) -> None:
    """
    Wait for the server to start and be ready to accept requests.
    """

    start_time = time.time()
    while True:
        try:
            response = requests.get(os.environ["API_URL"] + "/health")
            if response.status_code == 200:
                print("Server is ready.")
                return
        except requests.ConnectionError:
            pass
        
        if time.time() - start_time > timeout:
            print(f"Failed to start the server. Timeout after {timeout} seconds. Exiting.")
            exit(1)
        
        # print(f"Waiting for server to start... ({time.time() - start_time:.2f} seconds elapsed)")
        time.sleep(interval)
        
def should_skip_global_server():
    """Check if global server startup should be skipped"""
    return os.environ.get("SKIP_GLOBAL_SERVER") == "1"

def load_and_run_tests():
    """
    Load and run all tests in the test directory.
    """
    loader = unittest.TestLoader()
    start_dir = os.path.join(PROJECT_ROOT, "src", "property_record_web_scraping", "test")
    
    # Load all tests first
    all_tests = loader.discover(start_dir=start_dir, pattern="test_*.py", top_level_dir=start_dir)
    
    # Check if any tests require standalone server management
    has_standalone_tests = any(
        "test_directory_independence" in str(test)
        for test in all_tests
    )
    
    if has_standalone_tests:
        # Split tests into two suites
        standalone_suite = unittest.TestSuite()
        regular_suite = unittest.TestSuite()
        
        for test_group in all_tests:
            for test_case in test_group:
                if "test_directory_independence" in str(test_case):
                    standalone_suite.addTest(test_case)
                else:
                    regular_suite.addTest(test_case)
        
        runner = unittest.TextTestRunner(verbosity=2, buffer=True, tb_locals=True)
        
        # Run standalone tests first (they manage their own server)
        print("Running standalone server tests...")
        standalone_result = runner.run(standalone_suite)
        
        # Run regular tests with global server
        if regular_suite.countTestCases() > 0:
            print("Running regular tests with global server...")
            start_server()
            wait_server()
            regular_result = runner.run(regular_suite)
            stop_server()
            
            # Combine results
            standalone_result.testsRun += regular_result.testsRun
            standalone_result.failures.extend(regular_result.failures)
            standalone_result.errors.extend(regular_result.errors)
        
        return standalone_result
    else:
        # Original behavior for regular tests only
        runner = unittest.TextTestRunner(verbosity=2, buffer=True, tb_locals=True)
        return runner.run(all_tests)

def main():
    # Check start conditions
    assert_start_conditions()
    
    # Run the tests (server management now handled in load_and_run_tests)
    result = load_and_run_tests()

    # Exit with the appropriate status code
    sys.exit(0 if result.wasSuccessful() else 1)
    
if __name__ == "__main__":
    main()