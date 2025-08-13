import unittest, os, requests, time, sys, signal, logging

# Use centralized Config for path setup
from property_record_web_scraping.server.config_utils import Config
Config.setup_python_path()

# Import the server once the paths are set up
import property_record_web_scraping.server as server

# Set up project root using centralized Config
PROJECT_ROOT = Config.get_project_root()
RUN_TESTS_INDEPENDENTLY = False  # Set to False to use single global server for all tests
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
        server.build(run_immediately=True)
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
        os.kill(server_app_id, signal.SIGTERM)  # Send SIGTERM to gracefully stop the server
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
        

def load_and_run_tests():
    """
    Load and run all tests with standalone or global server instances.
    """
    loader = unittest.TestLoader()
    start_dir = os.path.join(PROJECT_ROOT, "src", "property_record_web_scraping", "test")
    
    # Discover all tests
    all_tests = loader.discover(start_dir=start_dir, pattern="test_health.py", top_level_dir=start_dir)
    
    runner = unittest.TextTestRunner(verbosity=2, buffer=True, tb_locals=True)
    
    if RUN_TESTS_INDEPENDENTLY:
        # Run each test module with its own server instance
        i = 0
        test_modules = list(all_tests)
        total_modules = len(test_modules)
        
        print(f"Found {total_modules} test modules to run independently")
        print("=" * 60)
        
        while i < len(test_modules):
            test_module = test_modules[i]
            module_name = str(test_module).split()[0].replace('<', '')
            
            # Progress indicator
            progress = (i + 1) / total_modules
            bar_length = 30
            filled_length = int(bar_length * progress)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            print(f"\n[{i+1}/{total_modules}] {bar} {progress:.1%}")
            print(f"Starting: {module_name}")
            print("-" * 40)
            
            # Start server for this test module
            print("🚀 Starting server...")
            start_server()
            wait_server()
            print("✓ Server ready")
            
            # Run the tests for this module
            print(f"🧪 Running tests in {module_name}...")
            result = runner.run(test_module)
            
            # Print test results summary
            print(f"📊 Results: {result.testsRun} tests run")
            if result.wasSuccessful():
                print("✅ All tests passed!")
            else:
                print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
                if result.failures:
                    print("   Failures:")
                    for test, _ in result.failures:
                        print(f"     - {test}")
                if result.errors:
                    print("   Errors:")
                    for test, _ in result.errors:
                        print(f"     - {test}")
            
            # Stop server after this test module
            print("🛑 Stopping server...")
            stop_server()
            print("✓ Server stopped")
            
            i += 1
        
        print("\n" + "=" * 60)
        print("🎉 All test modules completed!")
    else:
        # Run all tests with a single global server
        print("Running all tests with single global server")
        print("=" * 60)
        
        print("🚀 Starting global server...")
        start_server()
        wait_server()
        print("✓ Global server ready")
        
        print("🧪 Running all tests...")
        result = runner.run(all_tests)
        
        # Print test results summary
        print(f"📊 Results: {result.testsRun} tests run")
        if result.wasSuccessful():
            print("✅ All tests passed!")
        else:
            print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
        
        print("🛑 Stopping global server...")
        stop_server()
        print("✓ Global server stopped")
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed!")

def main():
    # Check start conditions
    assert_start_conditions()
    
    # Run the tests (server management now handled in load_and_run_tests)
    load_and_run_tests()

    # Exit successfully (individual test results are displayed by the runner)
    sys.exit(0)
    
if __name__ == "__main__":
    main()