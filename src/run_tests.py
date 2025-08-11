from pathlib import Path
import unittest, os, requests, server, time, sys, signal

# Add schema path to envrionemt
PROJECT_ROOT = Path(__file__).parent.absolute()  # Points to ./src
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
        app_path = os.path.join(PROJECT_ROOT, "app.py")
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
        
def load_and_run_tests():
    """
    Load and run all tests in the test directory.
    """
    loader = unittest.TestLoader()
    start_dir = os.path.join(PROJECT_ROOT, "test")  # Adjust path to your test directory
    tests = loader.discover(start_dir=start_dir, pattern="test_*.py", top_level_dir=start_dir)  # Adjust pattern if needed
    runner = unittest.TextTestRunner(verbosity=2, buffer=True, tb_locals=True)
    return runner.run(tests)

def main():
    # Check start conditions
    assert_start_conditions()
    
    # Start the server
    start_server()
    
    # Wait for the server to be ready
    wait_server()

    # Run the tests
    result = load_and_run_tests()

    # Stop the server after tests are done
    stop_server()

    # Exit with the appropriate status code
    sys.exit(0 if result.wasSuccessful() else 1)
    
if __name__ == "__main__":
    main()