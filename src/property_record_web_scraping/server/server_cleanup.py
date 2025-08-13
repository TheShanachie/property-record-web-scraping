import os, sys, signal, atexit, psutil, threading, time, requests, traceback
from typing import List, Optional, Dict, Any, Tuple


def server_cleanup(main_pid: int) -> None:
    """
    Perform cleanup actions for the server.
    """
    # Print the start of garbage cleanup.
    print("=" * 30)
    print("Checking for Garbage Chrome processes after server stop.")
    print("=" * 30)
    
    # Identify and collect metadata for garbage processes
    garbage_processes = _identify_garbage_chrome_processes(main_pid)
    before_metadata = _collect_process_metadata(garbage_processes)
    
    # Kill the processes
    _kill_garbage_chrome_processes(garbage_processes)
    
    # Collect metadata after killing
    after_metadata = _collect_process_metadata(garbage_processes)
    
    # Print statistics
    print()
    print(f"Found {len(garbage_processes)} garbage Chrome processes.")
    print(f"Before cleanup: {len(before_metadata)} processes")
    print(f"After cleanup: {len(after_metadata)} processes")
    print(f"Successfully cleaned up: {len(before_metadata) - len(after_metadata)} processes")
    print()

    # Print simple table
    print("=" * 50)
    print("Process cleanup results:")
    print("=" * 50)
    for i, (pid, name, status) in enumerate(before_metadata):
        still_running = any(p[0] == pid for p in after_metadata)
        status_str = "RUNNING" if still_running else "KILLED"
        print(f"{pid:<8} {name:<20} {status_str}")
    print("=" * 50)

def _identify_garbage_chrome_processes(main_pid: int) -> List[psutil.Process]:
    """
    Identify Chrome processes that are NOT subprocesses of the main process.
    These are considered "garbage" processes that may be orphaned.
    """
    try:
        # Get all subprocess PIDs of the main process
        main_process = psutil.Process(main_pid)
        subprocess_pids = {child.pid for child in main_process.children(recursive=True)}
        subprocess_pids.add(main_pid)  # Include main process itself
        
        # Find Chrome processes that are NOT subprocesses
        garbage_chrome_processes = []
        for proc in psutil.process_iter(attrs=['pid', 'name']):
            try:
                if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                    if proc.info['pid'] not in subprocess_pids:
                        garbage_chrome_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return garbage_chrome_processes
        
    except Exception as e:
        print(f"Error identifying garbage Chrome processes: {e}")
        return []

def _collect_process_metadata(processes: List[psutil.Process]) -> List[Tuple[int, str, str]]:
    """
    Collect metadata from a list of psutil.Process objects into tuples.
    
    Args:
        processes: List of psutil.Process objects
        
    Returns:
        List of tuples containing (pid, name, status) for each process
    """
    metadata = []
    for proc in processes:
        try:
            pid = proc.pid
            name = proc.name()
            status = proc.status()
            metadata.append((pid, name, status))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return metadata
    
def _kill_garbage_chrome_processes(garbage_processes: List[psutil.Process]) -> None:
    """
    Kill the identified garbage Chrome processes.
    """
    for proc in garbage_processes:
        try:
            proc.kill()
            print(f"Killed garbage Chrome process: {proc.info['pid']} - {proc.info['name']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue