import os, sys, signal, atexit, psutil, threading, time, requests, traceback
from typing import List, Optional, Dict, Any

class ProcessCleanupManager:
    """
    General cleanup manager parent class for rogue sub-process cleanup.
    """
    
    def __init__(self, api_url: str):
        """
        Initialize the cleanup manager.
        """
        self.api_url = api_url
        self.main_pid = None
        self.cleanup_registered = False
        self.cleaned_processes: Dict[Any, Any] = {}
        
    def register_cleanup(self, main_pid: int):
        """
        Register cleanup handlers for graceful exit.
        
        Args:
            main_pid: Main process PID to manage
        """
        self.main_pid = main_pid
        
        if not self.cleanup_registered:
            self.cleanup_registered = True
            atexit.register(self._cleanup)
            print(f"Cleanup handlers registered for main PID: {self.main_pid}")
        else:
            print("Cleanup handlers already registered, skipping re-registration.")
    
    
    def _get_subprocesses(self) -> List[psutil.Process]:
        """
        Get all subprocesses of the main process.
        """
        try:
            parent_process = psutil.Process(self.main_pid)
            return parent_process.children(recursive=True)
        except psutil.NoSuchProcess:
            print(f"Main process with PID {self.main_pid} does not exist.")
            return []
        except Exception as e:
            print(f"Error accessing main process {self.main_pid}: {e}")
            return []

    def _filter_chrome_processes(self, processes: List[psutil.Process]) -> List[psutil.Process]:
        """
        Filter Chrome processes from a list of processes.
        """
        chrome_processes = []
        for child in processes:
            try:
                name = child.name().lower()
                if 'chrome' in name:
                    chrome_processes.append(child)
            except psutil.NoSuchProcess:
                print(f"Process {child.pid} no longer exists.")
            except Exception as e:
                print(f"Error accessing process {child.pid}: {e}")
        return chrome_processes

    def _send_signal_to_processes(self, processes: List[psutil.Process], sig: int):
        """
        Send a signal to a list of processes.
        """
        for proc in processes:
            try:
                print(f"Sending signal {sig} to Chrome process PID {proc.pid} ({proc.name()})")
                proc.send_signal(sig)
            except psutil.NoSuchProcess:
                print(f"Process {proc.pid} no longer exists when sending signal.")
            except psutil.AccessDenied:
                print(f"Access denied to process {proc.pid}.")
            except Exception as e:
                print(f"Error sending signal to process {proc.pid}: {e}")

    def _kill_chrome_subprocesses(self, sig: int = signal.SIGTERM, timeout: int | None = None):
        """
        Kill all Chrome subprocesses of the current main_pid.

        Args:
            sig: Signal to send to the processes (default: SIGTERM)
            timeout: Maximum seconds to wait for graceful shutdown (default: None)

        Returns:
            Tuple of (gone, alive) processes
        """
        subprocesses = self._get_subprocesses()
        chrome_processes = self._filter_chrome_processes(subprocesses)

        if not chrome_processes:
            print("No Chrome subprocesses found.")
            return ([], [])

        self._send_signal_to_processes(chrome_processes, sig)
        gone, alive = psutil.wait_procs(chrome_processes, timeout=timeout)
        return (gone, alive)
    
    def _print_cleanup_results(self, gone: List[psutil.Process], alive: List[psutil.Process]):
        """
        Print the results of the cleanup operation.
        
        Args:
            gone: List of processes that were successfully killed
            alive: List of processes that are still running
        """
        gone_info = [proc.as_dict() for proc in gone]
        alive_info = [proc.as_dict() for proc in alive]
    
        print(f"Cleanup Results:\n",
              f"Processes gone: {len(gone_info)}\n",
              f"Processes alive: {len(alive_info)}\n",
              f"Gone processes: {gone_info}\n",
              f"Alive processes: {alive_info}")        
        
    def _cleanup(self):
        """
        Main cleanup function
        """
        assert self.main_pid is not None, "Main PID must be set before cleanup"
        assert self.cleanup_registered, "Cleanup handlers must be registered before cleanup"
        
        try:
            # Perform safe cleanup
            gone, alive = self._kill_chrome_subprocesses()
            self._print_cleanup_results(gone, alive)
            
        except Exception as e:
            # Log the exception details for debugging
            print(f"Error during cleanup: {e}")
            traceback.print_exc()
