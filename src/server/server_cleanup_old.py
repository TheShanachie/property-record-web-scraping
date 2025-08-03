import os
import signal
import psutil
import threading
import time
import requests
from typing import List, Optional, Dict, Any

class ProcessCleanupManager:
    """
    Comprehensive process cleanup manager for web scraping API.
    Handles cleanup of threads, Chrome instances, and child processes safely.
    """
    
    def __init__(self, api_url: str):
        """
        Initialize the cleanup manager.
        
        Args:
            api_url: API URL for health checks (optional)
        """
        self.api_url = api_url
        self.main_pid = None
        self.cleanup_registered = False
        
    def register_cleanup(self, main_pid: int):
        """
        Register cleanup handlers for graceful exit.
        
        Args:
            main_pid: Main process PID to manage
        """
        import atexit
        
        self.main_pid = main_pid
        
        if not self.cleanup_registered:
            atexit.register(self.cleanup_and_goodbye)
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            self.cleanup_registered = True
            print(f"🛡️  Cleanup handlers registered for PID {main_pid}")
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals (Ctrl+C, etc.)"""
        signal_names = {
            signal.SIGINT: "SIGINT (Ctrl+C)",
            signal.SIGTERM: "SIGTERM",
        }
        signal_name = signal_names.get(signum, f"Signal {signum}")
        print(f"\n⚡ Received {signal_name}. Initiating cleanup...")
        import sys
        sys.exit(1)
    
    def cleanup_and_goodbye(self):
        """
        Main cleanup function - comprehensive resource cleanup with safety checks.
        """
        print("\n" + "="*60)
        print("🧹 COMPREHENSIVE CLEANUP AND EXIT ROUTINE")
        print("="*60)
        
        if self.main_pid is None:
            print("No process registered for cleanup.")
            self._print_goodbye()
            return
        
        try:
            # Perform safe cleanup
            results = self.safe_cleanup_all_resources(timeout=30)
            
            # Print detailed results
            self._print_cleanup_results(results)
            
            # Final API check
            self._final_api_status_check()
            
        except Exception as e:
            print(f"💥 Error during cleanup: {e}")
            import traceback
            traceback.print_exc()
        
        self._print_goodbye()
    
    def safe_cleanup_all_resources(self, timeout: int = 30) -> Dict[str, Any]:
        """
        Safely clean up all project resources with graceful shutdown preference.
        
        Args:
            timeout: Maximum seconds to wait for graceful shutdown
            
        Returns:
            Dict containing cleanup results and statistics
        """
        results = {
            "success": True,
            "threads_found": 0,
            "threads_stopped": 0,
            "chrome_processes_found": 0,
            "chrome_processes_killed": 0,
            "child_processes_found": 0,
            "child_processes_killed": 0,
            "warnings": [],
            "errors": [],
            "main_process_terminated": False
        }
        
        try:
            main_process = psutil.Process(self.main_pid)
            print(f"🎯 Starting cleanup for process tree rooted at PID {self.main_pid}")
            
            # Step 1: Try graceful application shutdown first
            print("🔄 Step 1: Attempting graceful application shutdown...")
            if self._try_graceful_shutdown(main_process, timeout // 3):
                print("✅ Application shut down gracefully - cleanup complete!")
                results["main_process_terminated"] = True
                return results
            
            print("⚠️  Graceful shutdown incomplete, proceeding with targeted cleanup...")
            
            # Step 2: Stop Python threads
            print("🧵 Step 2: Stopping Python threads...")
            thread_results = self._stop_python_threads()
            results.update(thread_results)
            
            # Step 3: Clean up our Chrome instances only
            print("🌐 Step 3: Cleaning up Chrome instances...")
            chrome_results = self._safe_cleanup_chrome_processes(main_process, timeout // 3)
            results.update(chrome_results)
            
            # Step 4: Clean up other child processes
            print("👶 Step 4: Cleaning up child processes...")
            child_results = self._safe_cleanup_child_processes(main_process, timeout // 3)
            results.update(child_results)
            
            # Step 5: Final attempt on main process
            print("🎯 Step 5: Final main process cleanup...")
            if main_process.is_running():
                main_process.terminate()
                try:
                    main_process.wait(timeout=5)
                    print("✅ Main process terminated gracefully")
                    results["main_process_terminated"] = True
                except psutil.TimeoutExpired:
                    results["warnings"].append("Main process still running after termination signal")
                    print("⚠️  Main process did not terminate gracefully")
            
        except psutil.NoSuchProcess:
            print(f"ℹ️  Process {self.main_pid} not found (already terminated)")
            results["main_process_terminated"] = True
        except Exception as e:
            error_msg = f"Cleanup error: {e}"
            results["errors"].append(error_msg)
            results["success"] = False
            print(f"💥 {error_msg}")
        
        return results
    
    def _try_graceful_shutdown(self, main_process: psutil.Process, timeout: int) -> bool:
        """
        Attempt graceful shutdown by sending SIGTERM and waiting.
        
        Returns:
            True if process shut down gracefully, False otherwise
        """
        try:
            if not main_process.is_running():
                return True
                
            print(f"   Sending SIGTERM to PID {main_process.pid}...")
            main_process.terminate()
            
            # Wait for graceful shutdown
            try:
                main_process.wait(timeout=timeout)
                return True
            except psutil.TimeoutExpired:
                print(f"   Process did not terminate within {timeout} seconds")
                return False
                
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"   Could not terminate process: {e}")
            return False
    
    def _stop_python_threads(self) -> Dict[str, Any]:
        """
        Attempt to stop Python threads (limited by Python's threading model).
        
        Returns:
            Dict with thread cleanup results
        """
        results = {"threads_found": 0, "threads_stopped": 0, "errors": []}
        
        try:
            all_threads = threading.enumerate()
            active_threads = [t for t in all_threads if t != threading.main_thread() and t.is_alive()]
            results["threads_found"] = len(active_threads)
            
            print(f"   Found {len(active_threads)} active threads")
            
            for thread in active_threads:
                try:
                    thread_name = getattr(thread, 'name', 'Unknown')
                    print(f"   Thread: {thread_name} (alive: {thread.is_alive()})")
                    
                    # Note: Python doesn't allow forceful thread termination
                    # We can only request graceful shutdown
                    if hasattr(thread, '_stop'):
                        thread._stop()
                        results["threads_stopped"] += 1
                    
                except Exception as e:
                    results["errors"].append(f"Thread cleanup error: {e}")
            
            if results["threads_found"] > 0:
                print(f"   ⚠️  Python threads cannot be force-stopped. {results['threads_found']} may remain.")
            
        except Exception as e:
            results["errors"].append(f"Thread enumeration error: {e}")
        
        return results
    
    def _safe_cleanup_chrome_processes(self, main_process: psutil.Process, timeout: int) -> Dict[str, Any]:
        """
        Safely clean up Chrome processes that belong to this project only.
        
        Args:
            main_process: Main process to check children of
            timeout: Timeout for graceful shutdown
            
        Returns:
            Dict with Chrome cleanup results
        """
        results = {"chrome_processes_found": 0, "chrome_processes_killed": 0, "errors": []}
        
        try:
            chrome_processes = []
            
            # Find Chrome processes in our process tree
            all_children = main_process.children(recursive=True)
            
            for child in all_children:
                try:
                    if self._is_our_chrome_process(child):
                        chrome_processes.append(child)
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            results["chrome_processes_found"] = len(chrome_processes)
            print(f"   Found {len(chrome_processes)} Chrome processes in our tree")
            
            # Terminate Chrome processes gracefully first
            for proc in chrome_processes:
                try:
                    proc_info = f"PID {proc.pid} ({proc.name()})"
                    print(f"   🎯 Terminating Chrome process: {proc_info}")
                    
                    proc.terminate()
                    
                    # Wait for graceful shutdown
                    try:
                        proc.wait(timeout=min(3, timeout))
                        print(f"      ✅ Gracefully terminated: {proc_info}")
                        results["chrome_processes_killed"] += 1
                    except psutil.TimeoutExpired:
                        print(f"      ⚡ Force killing: {proc_info}")
                        proc.kill()
                        results["chrome_processes_killed"] += 1
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    results["errors"].append(f"Chrome cleanup error for PID {proc.pid}: {e}")
        
        except Exception as e:
            results["errors"].append(f"Chrome process discovery error: {e}")
        
        return results
    
    def _is_our_chrome_process(self, process: psutil.Process) -> bool:
        """
        Determine if a Chrome process belongs to our project.
        
        Args:
            process: Process to check
            
        Returns:
            True if it's our Chrome process, False otherwise
        """
        try:
            name = process.name().lower()
            
            # Must be a Chrome-related process
            if not any(chrome_name in name for chrome_name in ['chrome', 'chromium', 'chromedriver']):
                return False
            
            # Check command line for our project indicators
            cmdline = ' '.join(process.cmdline()).lower()
            
            project_indicators = [
                'chromedriver',
                'property-record-web-scraping',
                'selenium',
                '--remote-debugging-port',  # Common Selenium flag
                '--disable-dev-shm-usage',  # Common headless flag
                '--no-sandbox'  # Common Docker/headless flag
            ]
            
            return any(indicator in cmdline for indicator in project_indicators)
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
    
    def _safe_cleanup_child_processes(self, main_process: psutil.Process, timeout: int) -> Dict[str, Any]:
        """
        Clean up non-Chrome child processes.
        
        Args:
            main_process: Main process to check children of
            timeout: Timeout for graceful shutdown
            
        Returns:
            Dict with child process cleanup results
        """
        results = {"child_processes_found": 0, "child_processes_killed": 0, "errors": []}
        
        try:
            # Get all child processes
            children = main_process.children(recursive=True)
            
            # Filter out Chrome processes (handled separately)
            non_chrome_children = []
            for child in children:
                try:
                    if not self._is_our_chrome_process(child):
                        non_chrome_children.append(child)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            results["child_processes_found"] = len(non_chrome_children)
            print(f"   Found {len(non_chrome_children)} non-Chrome child processes")
            
            # Terminate children gracefully
            for child in non_chrome_children:
                try:
                    proc_info = f"PID {child.pid} ({child.name()})"
                    print(f"   🎯 Terminating child: {proc_info}")
                    child.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Wait for graceful shutdown
            if non_chrome_children:
                gone, alive = psutil.wait_procs(non_chrome_children, timeout=timeout)
                results["child_processes_killed"] = len(gone)
                
                # Force kill any remaining
                for proc in alive:
                    try:
                        proc_info = f"PID {proc.pid} ({proc.name()})"
                        print(f"      ⚡ Force killing: {proc_info}")
                        proc.kill()
                        results["child_processes_killed"] += 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        results["child_processes_killed"] += 1  # Assume it died
        
        except Exception as e:
            results["errors"].append(f"Child process cleanup error: {e}")
        
        return results
    
    def _final_api_status_check(self):
        """Check if API is still responding after cleanup."""
        if not self.api_url:
            print("🔍 No API URL configured - skipping status check")
            return
        
        print("🔍 Final API status check...")
        try:
            response = requests.get(f"{self.api_url}/health", timeout=3)
            if response.status_code == 200:
                print("⚠️  WARNING: API is still responding!")
                print("   Some processes may still be running.")
                self._offer_nuclear_option()
            else:
                print("✅ API is not responding (expected)")
        except requests.exceptions.RequestException:
            print("✅ API is not responding (expected)")
        except Exception as e:
            print(f"❓ Could not check API status: {e}")
    
    def _offer_nuclear_option(self):
        """Offer nuclear Chrome cleanup option with user confirmation."""
        print("\n💣 Nuclear Chrome cleanup available (kills ALL Chrome processes)")
        print("   ⚠️  WARNING: This will close all Chrome windows on your system!")
        
        try:
            # Only offer in interactive mode
            if os.isatty(0):  # Check if running in terminal
                response = input("   Execute nuclear cleanup? (y/N): ").strip().lower()
                if response in ['y', 'yes']:
                    nuclear_results = self.nuclear_chrome_cleanup()
                    print(f"   💥 Nuclear cleanup completed: {nuclear_results['chrome_processes_killed']} processes killed")
                else:
                    print("   ❌ Nuclear cleanup cancelled")
            else:
                print("   ⏭️  Running non-interactively - skipping nuclear option")
        except Exception as e:
            print(f"   ❌ Error in nuclear option: {e}")
    
    def nuclear_chrome_cleanup(self) -> Dict[str, Any]:
        """
        Nuclear option: Kill ALL Chrome processes on the system.
        Use with extreme caution!
        
        Returns:
            Dict with nuclear cleanup results
        """
        results = {"chrome_processes_found": 0, "chrome_processes_killed": 0, "errors": []}
        
        chrome_names = ['chrome', 'chromium', 'google-chrome', 'chromedriver']
        
        print("💥 Executing nuclear Chrome cleanup...")
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                name = proc.info['name'].lower()
                if any(chrome_name in name for chrome_name in chrome_names):
                    results["chrome_processes_found"] += 1
                    print(f"   💥 Killing: {proc.info['name']} (PID {proc.info['pid']})")
                    
                    proc.terminate()
                    try:
                        proc.wait(timeout=2)
                    except psutil.TimeoutExpired:
                        proc.kill()
                    
                    results["chrome_processes_killed"] += 1
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                results["errors"].append(f"Nuclear cleanup error: {e}")
        
        return results
    
    def _print_cleanup_results(self, results: Dict[str, Any]):
        """Print detailed cleanup results."""
        print("\n📊 CLEANUP SUMMARY:")
        print(f"   🧵 Threads found/stopped: {results['threads_found']}/{results['threads_stopped']}")
        print(f"   🌐 Chrome processes found/killed: {results['chrome_processes_found']}/{results['chrome_processes_killed']}")
        print(f"   👶 Child processes found/killed: {results['child_processes_found']}/{results['child_processes_killed']}")
        print(f"   🎯 Main process terminated: {'✅' if results['main_process_terminated'] else '❌'}")
        
        if results['warnings']:
            print(f"   ⚠️  Warnings ({len(results['warnings'])}):")
            for warning in results['warnings']:
                print(f"      - {warning}")
        
        if results['errors']:
            print(f"   💥 Errors ({len(results['errors'])}):")
            for error in results['errors']:
                print(f"      - {error}")
        
        overall_status = "✅ SUCCESS" if results['success'] and not results['errors'] else "⚠️  PARTIAL"
        print(f"   📋 Overall status: {overall_status}")
    
    def _print_goodbye(self):
        """Print friendly goodbye message."""
        print("\n🎭 Thank you for using the Property Record Web Scraping API!")
        print("   All available resources have been cleaned up.")
        print("   Have a great day! 👋")
        print("="*60)

# Convenience functions for easy usage
def setup_cleanup_manager(main_pid: int, api_url: str = None) -> ProcessCleanupManager:
    """
    Convenience function to set up cleanup manager with handlers.
    
    Args:
        main_pid: Main process PID to manage
        api_url: API URL for health checks (optional)
        
    Returns:
        Configured ProcessCleanupManager instance
    """
    manager = ProcessCleanupManager(api_url)
    manager.register_cleanup(main_pid)
    return manager

def manual_cleanup(main_pid: int, api_url: str = None, timeout: int = 30) -> Dict[str, Any]:
    """
    Manually trigger cleanup without registering handlers.
    
    Args:
        main_pid: Main process PID to clean up
        api_url: API URL for health checks (optional)
        timeout: Cleanup timeout in seconds
        
    Returns:
        Cleanup results dictionary
    """
    manager = ProcessCleanupManager(api_url)
    manager.main_pid = main_pid
    return manager.safe_cleanup_all_resources(timeout)