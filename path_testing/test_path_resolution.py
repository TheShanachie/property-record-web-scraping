#!/usr/bin/env python3
"""
Test script to verify Config path resolution works correctly.
This script tests the YAML config path resolution from different working directories.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the src directory to Python path for absolute imports
script_dir = Path(__file__).parent.parent.absolute()  # Go up from path_testing to project root
src_dir = script_dir / "src"
sys.path.insert(0, str(src_dir))

# Now we can import the Config class
from property_record_web_scraping.server.config_utils import Config

def test_path_resolution():
    """Test Config path resolution functionality."""
    
    print("🔍 Testing Config Path Resolution")
    print(f"Project root: {script_dir}")
    
    # Test 1: Initialize Config and check project root
    print("\n1. Testing project root detection...")
    project_root = Config.get_project_root()
    print(f"   Detected project root: {project_root}")
    
    # Verify pyproject.toml exists
    pyproject_path = project_root / "pyproject.toml"
    if pyproject_path.exists():
        print("   ✅ pyproject.toml found - correct project root")
    else:
        print("   ❌ pyproject.toml NOT found - incorrect project root")
        return False
    
    # Test 2: Test resolve_path method directly
    print("\n2. Testing resolve_path method...")
    test_paths = [
        "./src/property_record_web_scraping/server/build/bin/chrome-linux64/chrome",
        "./src/property_record_web_scraping/server/logs/",
        "./src/property_record_web_scraping/server/logs/tempempty/",
        "./src/property_record_web_scraping/server/build/bin/chromedriver-linux64/chromedriver"
    ]
    
    for test_path in test_paths:
        resolved = Config.resolve_path(test_path)
        print(f"   '{test_path}' → '{resolved}'")
        if resolved.is_absolute():
            print(f"   ✅ Resolved to absolute path")
        else:
            print(f"   ❌ Still relative path - resolution failed")
            return False
    
    # Test 3: Load and check actual config files
    print("\n3. Testing actual YAML config loading...")
    
    # Initialize config (this should resolve all paths in YAML files)
    Config.initialize()
    
    # Test selenium_chrome config
    selenium_config = Config.get_config(['selenium_chrome'])
    chrome_paths = selenium_config.get('chrome-paths', {})
    print(f"   Chrome path from config: {chrome_paths.get('chrome-binary-path')}")
    print(f"   ChromeDriver path from config: {chrome_paths.get('chrome-driver-path')}")
    
    # Verify these are now absolute paths
    chrome_path = chrome_paths.get('chrome-binary-path')
    if chrome_path and Path(chrome_path).is_absolute():
        print("   ✅ Chrome path resolved to absolute")
    else:
        print(f"   ❌ Chrome path still relative: {chrome_path}")
        return False
        
    chromedriver_path = chrome_paths.get('chrome-driver-path')
    if chromedriver_path and Path(chromedriver_path).is_absolute():
        print("   ✅ ChromeDriver path resolved to absolute")
    else:
        print(f"   ❌ ChromeDriver path still relative: {chromedriver_path}")
        return False
    
    # Test logging config
    log_dir = Config.get_config(['logging_utils', 'log-dir-path'])
    print(f"   Log directory from config: {log_dir}")
    if log_dir and Path(log_dir).is_absolute():
        print("   ✅ Log directory resolved to absolute")
    else:
        print(f"   ❌ Log directory still relative: {log_dir}")
        return False
    
    # Test download directory in chrome-paths
    download_dir = chrome_paths.get('download-directory-path')
    print(f"   Download directory from config: {download_dir}")
    if download_dir and Path(download_dir).is_absolute():
        print("   ✅ Download directory resolved to absolute")
    else:
        print(f"   ❌ Download directory still relative: {download_dir}")
        return False
    
    print("\n✅ All path resolution tests passed!")
    return True

def test_from_different_directory():
    """Test path resolution from a different working directory."""
    
    print("\n🔄 Testing from different working directory...")
    
    # Save current directory
    original_cwd = os.getcwd()
    
    try:
        # Create a temporary directory and change to it
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            print(f"Changed working directory to: {temp_dir}")
            
            # Force reload Config to test from new directory
            Config._instance = None
            Config._config = None
            Config._project_root = None
            Config._package_root = None
            
            # Test path resolution from this directory
            project_root = Config.get_project_root()
            print(f"Project root from temp dir: {project_root}")
            
            # Verify it still finds the correct project root
            pyproject_path = project_root / "pyproject.toml"
            if pyproject_path.exists():
                print("   ✅ Still found correct project root from different CWD")
                return True
            else:
                print("   ❌ Failed to find correct project root from different CWD")
                return False
                
    finally:
        # Always restore original directory
        os.chdir(original_cwd)
        # Reset Config for clean state
        Config._instance = None
        Config._config = None
        Config._project_root = None
        Config._package_root = None

def main():
    """Run all path resolution tests."""
    
    print("=" * 60)
    print("CONFIG PATH RESOLUTION VERIFICATION")
    print("=" * 60)
    
    # Test from current directory
    success1 = test_path_resolution()
    
    # Test from different directory
    success2 = test_from_different_directory()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 ALL TESTS PASSED - Path resolution is working correctly!")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Path resolution needs fixes")
        return 1

if __name__ == "__main__":
    sys.exit(main())