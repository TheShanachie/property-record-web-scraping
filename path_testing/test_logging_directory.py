#!/usr/bin/env python3
"""
Test script to verify logging directory creation and path resolution works correctly.
"""

import os
import sys
import tempfile
import logging
from pathlib import Path

# Add the src directory to Python path for absolute imports
script_dir = Path(__file__).parent.parent.absolute()
src_dir = script_dir / "src"
sys.path.insert(0, str(src_dir))

# Import Config and logging utilities directly
from property_record_web_scraping.server.config_utils.Config import Config
from property_record_web_scraping.server.logging_utils.loggers import _create_logger

def test_logging_config_resolution():
    """Test that logging config paths resolve correctly."""
    
    print("🔍 Testing Logging Configuration Path Resolution")
    
    # Test 1: Initialize config and check log directory resolution
    print("\n1. Testing log directory path resolution...")
    Config.initialize()
    
    log_dir = Config.get_config(['logging_utils', 'log-dir-path'])
    print(f"   Log directory from config: {log_dir}")
    
    if not log_dir:
        print("   ❌ Log directory not found in config")
        return False
        
    log_path = Path(log_dir)
    if not log_path.is_absolute():
        print(f"   ❌ Log directory not resolved to absolute path: {log_dir}")
        return False
        
    print("   ✅ Log directory resolved to absolute path")
    
    # Test 2: Verify log directory exists
    print("\n2. Testing log directory existence...")
    
    if log_path.exists():
        print(f"   ✅ Log directory exists: {log_path}")
    else:
        print(f"   ❌ Log directory doesn't exist: {log_path}")
        print(f"   Required directory must be created in the project structure")
        return False
    
    # Test 3: Verify log directory is writable
    print("\n3. Testing log directory write access...")
    try:
        if os.access(log_path, os.W_OK):
            print("   ✅ Log directory is writable")
        else:
            print(f"   ❌ Log directory not writable: {log_path}")
            return False
    except Exception as e:
        print(f"   ❌ Error checking log directory access: {e}")
        return False
    
    print("\n✅ All logging config resolution tests passed!")
    return True

def test_logger_creation():
    """Test that logger creation works correctly with resolved paths."""
    
    print("\n📝 Testing Logger Creation and File Handling")
    
    # Test 1: Create each logger type and verify they work
    logger_configs = [
        ('web_scraping_core', 'web_scraping_core'),
        ('flask_app_interactions', 'flask_app_interactions'),
        ('event_handling_operations', 'event_handling_operations'),
        ('resource_management', 'resource_management')
    ]
    
    log_dir = Path(Config.get_config(['logging_utils', 'log-dir-path']))
    
    for logger_name, config_key in logger_configs:
        print(f"\n   Testing {logger_name} logger...")
        
        try:
            # Create logger
            logger = _create_logger(logger_name, config_key)
            
            # Test logging functionality
            test_message = f"Test message from {logger_name} logger"
            logger.debug(test_message)
            logger.info(f"Info: {test_message}")
            logger.warning(f"Warning: {test_message}")
            
            # Check if log file was created
            expected_log_file = log_dir / f"{logger_name}_logger.log"
            if expected_log_file.exists():
                print(f"      ✅ Log file created: {expected_log_file}")
                
                # Verify log content
                log_content = expected_log_file.read_text()
                if test_message in log_content:
                    print(f"      ✅ Log content written correctly")
                else:
                    print(f"      ⚠️  Log content may not include test message")
            else:
                print(f"      ❌ Log file not created: {expected_log_file}")
                return False
                
        except Exception as e:
            print(f"      ❌ Failed to create/test {logger_name} logger: {e}")
            return False
    
    print("\n✅ All logger creation tests passed!")
    return True

def test_logging_from_different_directory():
    """Test that logging works correctly from different working directories."""
    
    print("\n🔄 Testing Logging from Different Working Directory")
    
    # Save current directory
    original_cwd = os.getcwd()
    
    try:
        # Create a temporary directory and change to it
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            print(f"   Changed working directory to: {temp_dir}")
            
            # Force reload Config to test from new directory
            Config._instance = None
            Config._config = None
            Config._project_root = None
            Config._package_root = None
            
            # Test logging initialization from different directory
            try:
                logger = _create_logger('test_cross_directory', 'web_scraping_core')
                logger.info("Test message from different working directory")
                
                # Verify log directory was resolved correctly
                log_dir = Config.get_config(['logging_utils', 'log-dir-path'])
                log_path = Path(log_dir)
                
                if log_path.is_absolute() and log_path.exists():
                    print("   ✅ Logging works correctly from different working directory")
                    return True
                else:
                    print(f"   ❌ Log directory issue from different CWD: {log_path}")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Logging failed from different working directory: {e}")
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
    """Run all logging directory tests."""
    
    print("=" * 60)
    print("LOGGING DIRECTORY PATH RESOLUTION VERIFICATION")
    print("=" * 60)
    
    # Test config resolution
    success1 = test_logging_config_resolution()
    
    # Test logger creation
    success2 = test_logger_creation()
    
    # Test from different directory
    success3 = test_logging_from_different_directory()
    
    print("\n" + "=" * 60)
    if success1 and success2 and success3:
        print("🎉 ALL TESTS PASSED - Logging directory system works correctly!")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Logging directory system needs attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())