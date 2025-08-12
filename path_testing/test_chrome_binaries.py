#!/usr/bin/env python3
"""
Test script to verify Chrome/ChromeDriver binaries are correctly resolved and functional.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the src directory to Python path for absolute imports
script_dir = Path(__file__).parent.parent.absolute()
src_dir = script_dir / "src"
sys.path.insert(0, str(src_dir))

# Import Config directly
from property_record_web_scraping.server.config_utils.Config import Config

def test_chrome_binaries():
    """Test that Chrome and ChromeDriver binaries exist and are executable."""
    
    print("🔍 Testing Chrome/ChromeDriver Binary Resolution")
    
    # Initialize config to get resolved paths
    Config.initialize()
    selenium_config = Config.get_config(['selenium_chrome'])
    
    # Test Chrome binary
    print("\n1. Testing Chrome binary...")
    chrome_path = selenium_config.get('chrome-path')
    print(f"   Chrome path from config: {chrome_path}")
    
    if not chrome_path:
        print("   ❌ Chrome path not found in config")
        return False
        
    chrome_file = Path(chrome_path)
    if not chrome_file.exists():
        print(f"   ❌ Chrome binary does not exist at: {chrome_path}")
        return False
        
    if not chrome_file.is_file():
        print(f"   ❌ Chrome path is not a file: {chrome_path}")
        return False
        
    if not os.access(chrome_path, os.X_OK):
        print(f"   ❌ Chrome binary is not executable: {chrome_path}")
        return False
        
    print("   ✅ Chrome binary exists and is executable")
    
    # Test ChromeDriver binary
    print("\n2. Testing ChromeDriver binary...")
    chromedriver_path = selenium_config.get('chrome-driver-path')
    print(f"   ChromeDriver path from config: {chromedriver_path}")
    
    if not chromedriver_path:
        print("   ❌ ChromeDriver path not found in config")
        return False
        
    chromedriver_file = Path(chromedriver_path)
    if not chromedriver_file.exists():
        print(f"   ❌ ChromeDriver binary does not exist at: {chromedriver_path}")
        return False
        
    if not chromedriver_file.is_file():
        print(f"   ❌ ChromeDriver path is not a file: {chromedriver_path}")
        return False
        
    if not os.access(chromedriver_path, os.X_OK):
        print(f"   ❌ ChromeDriver binary is not executable: {chromedriver_path}")
        return False
        
    print("   ✅ ChromeDriver binary exists and is executable")
    
    # Test Chrome version
    print("\n3. Testing Chrome functionality...")
    try:
        result = subprocess.run([chrome_path, '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"   ✅ Chrome version: {version}")
        else:
            print(f"   ❌ Chrome version check failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Chrome version check error: {e}")
        return False
    
    # Test ChromeDriver version
    print("\n4. Testing ChromeDriver functionality...")
    try:
        result = subprocess.run([chromedriver_path, '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"   ✅ ChromeDriver version: {version}")
        else:
            print(f"   ❌ ChromeDriver version check failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ ChromeDriver version check error: {e}")
        return False
    
    print("\n✅ All Chrome/ChromeDriver binary tests passed!")
    return True

def test_build_directory_structure():
    """Test that build directory structure is correct."""
    
    print("\n🏗️  Testing Build Directory Structure")
    
    build_dir = Config.get_build_dir()
    print(f"   Build directory: {build_dir}")
    
    if not build_dir.exists():
        print(f"   ❌ Build directory does not exist: {build_dir}")
        return False
        
    # Check for expected subdirectories
    chrome_dir = build_dir / "chrome-linux64"
    chromedriver_dir = build_dir / "chromedriver-linux64"
    
    if not chrome_dir.exists():
        print(f"   ❌ Chrome directory missing: {chrome_dir}")
        return False
        
    if not chromedriver_dir.exists():
        print(f"   ❌ ChromeDriver directory missing: {chromedriver_dir}")
        return False
        
    print("   ✅ Build directory structure is correct")
    return True

def main():
    """Run all Chrome/ChromeDriver tests."""
    
    print("=" * 60)
    print("CHROME/CHROMEDRIVER BINARY VERIFICATION")
    print("=" * 60)
    
    # Test build directory structure
    success1 = test_build_directory_structure()
    
    # Test Chrome binaries
    success2 = test_chrome_binaries()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 ALL TESTS PASSED - Chrome/ChromeDriver binaries are working correctly!")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Chrome/ChromeDriver binaries need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())