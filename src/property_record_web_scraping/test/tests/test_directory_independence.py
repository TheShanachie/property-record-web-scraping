import unittest
import os
import subprocess
import signal
import time
import tempfile
import requests
from pathlib import Path

# Signal to run_tests.py that this test manages its own server
os.environ["SKIP_GLOBAL_SERVER"] = "1"
os.environ["STANDALONE_SERVER_TEST"] = "1"


class TestDirectoryIndependence(unittest.TestCase):
    """Test that the app can be run from any directory with valid environment"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.api_url = os.environ.get('API_URL', 'http://localhost:5000/api/v1')
        cls.project_root = Path(os.environ.get('PROJECT_ROOT', '')).absolute()
        cls.app_path = cls.project_root / "src" / "property_record_web_scraping" / "app.py"
        cls.test_processes = []
        
        # Verify the app path exists
        if not cls.app_path.exists():
            raise FileNotFoundError(f"App file not found at {cls.app_path}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up any remaining processes"""
        for process in cls.test_processes:
            try:
                if process.poll() is None:  # Process is still running
                    process.terminate()
                    process.wait(timeout=5)
            except (subprocess.TimeoutExpired, OSError):
                try:
                    process.kill()
                except OSError:
                    pass
    
    def setUp(self):
        """Ensure port is free before each test"""
        self.assertFalse(self._is_port_in_use(5000), "Port 5000 is already in use")
    
    def tearDown(self):
        """Clean up after each test"""
        self._cleanup_processes()
    
    def _is_port_in_use(self, port: int) -> bool:
        """Check if a port is currently in use"""
        result = os.system(f"lsof -i :{port} > /dev/null 2>&1")
        return result == 0
    
    def _cleanup_processes(self):
        """Kill any running test processes"""
        for process in self.test_processes:
            try:
                if process.poll() is None:  # Process is still running
                    process.terminate()
                    process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                try:
                    process.kill()
                    process.wait(timeout=2)
                except (subprocess.TimeoutExpired, OSError):
                    pass
            except OSError:
                pass
        self.test_processes.clear()
    
    def _start_app_from_directory(self, working_dir: Path, timeout: int = 30) -> subprocess.Popen:
        """Start the app from a specific directory and return the process"""
        env = os.environ.copy()
        env['PROJECT_ROOT'] = str(self.project_root)
        
        # Start the app process from the specified directory
        process = subprocess.Popen(
            [os.sys.executable, str(self.app_path)],
            cwd=str(working_dir),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid  # Create new process group for easier cleanup
        )
        
        self.test_processes.append(process)
        return process
    
    def _wait_for_health_response(self, timeout: int = 30) -> bool:
        """Wait for the app to respond to health checks"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.api_url}/health", timeout=2)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        return False
    
    def _test_health_from_directory(self, test_dir: Path, description: str):
        """Helper method to test app health from a specific directory"""
        with self.subTest(directory=str(test_dir), description=description):
            # Start app from test directory
            process = self._start_app_from_directory(test_dir)
            
            try:
                # Wait for app to be ready
                self.assertTrue(
                    self._wait_for_health_response(),
                    f"App failed to start or respond to health check when run from {test_dir}"
                )
                
                # Make health request
                response = requests.get(f"{self.api_url}/health", timeout=5)
                
                # Verify health response
                self.assertEqual(response.status_code, 200, 
                               f"Health check failed when app run from {test_dir}")
                
                health_data = response.json()
                self.assertIn('driver_pool', health_data,
                             f"Health response missing driver_pool when app run from {test_dir}")
                
            finally:
                # Clean up this specific process
                try:
                    if process.poll() is None:
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                        process.wait(timeout=5)
                except (subprocess.TimeoutExpired, OSError, ProcessLookupError):
                    try:
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    except (OSError, ProcessLookupError):
                        pass
                
                # Wait a moment for port to be freed
                time.sleep(2)
    
    def test_app_runs_from_project_root(self):
        """Test app can run from project root directory"""
        self._test_health_from_directory(
            self.project_root,
            "Running from project root"
        )
    
    def test_app_runs_from_parent_directory(self):
        """Test app can run from parent directory of project"""
        parent_dir = self.project_root.parent
        self._test_health_from_directory(
            parent_dir,
            "Running from parent directory"
        )
    
    def test_app_runs_from_temp_directory(self):
        """Test app can run from a temporary directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            self._test_health_from_directory(
                temp_path,
                "Running from temporary directory"
            )
    
    def test_app_runs_from_home_directory(self):
        """Test app can run from user home directory"""
        home_dir = Path.home()
        self._test_health_from_directory(
            home_dir,
            "Running from home directory"
        )
    
    def test_app_runs_from_src_directory(self):
        """Test app can run from src directory"""
        src_dir = self.project_root / "src"
        if src_dir.exists():
            self._test_health_from_directory(
                src_dir,
                "Running from src directory"
            )
        else:
            self.skipTest("src directory does not exist")