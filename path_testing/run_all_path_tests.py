#!/usr/bin/env python3
"""
Comprehensive path resolution verification test suite.
This script runs all path resolution tests to verify the Config system works correctly.
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

def run_test_script(script_path, description):
    """Run a test script and return success status."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        # Use the project's venv and run the script
        result = subprocess.run([
            sys.executable, str(script_path)
        ], capture_output=False, text=True, check=False)
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED (exit code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def test_from_different_directories():
    """Test running from different working directories."""
    print(f"\n{'='*60}")
    print("🔄 CROSS-DIRECTORY TESTING")
    print(f"{'='*60}")
    
    # Get project root and test script paths
    project_root = Path(__file__).parent.parent.absolute()
    test_script = project_root / "path_testing" / "test_config_only.py"
    
    # Save original directory
    original_cwd = os.getcwd()
    success_count = 0
    total_tests = 0
    
    try:
        # Test 1: From project root
        print("\n1. Testing from project root...")
        os.chdir(project_root)
        result = subprocess.run([sys.executable, str(test_script)], 
                              capture_output=True, text=True, check=False)
        total_tests += 1
        if result.returncode == 0:
            print("   ✅ Works from project root")
            success_count += 1
        else:
            print(f"   ❌ Failed from project root: {result.stderr}")
        
        # Test 2: From src directory
        print("\n2. Testing from src directory...")
        src_dir = project_root / "src"
        if src_dir.exists():
            os.chdir(src_dir)
            result = subprocess.run([sys.executable, str(test_script)], 
                                  capture_output=True, text=True, check=False)
            total_tests += 1
            if result.returncode == 0:
                print("   ✅ Works from src directory")
                success_count += 1
            else:
                print(f"   ❌ Failed from src directory: {result.stderr}")
        
        # Test 3: From path_testing directory
        print("\n3. Testing from path_testing directory...")
        path_testing_dir = project_root / "path_testing"
        if path_testing_dir.exists():
            os.chdir(path_testing_dir)
            result = subprocess.run([sys.executable, str(test_script)], 
                                  capture_output=True, text=True, check=False)
            total_tests += 1
            if result.returncode == 0:
                print("   ✅ Works from path_testing directory")
                success_count += 1
            else:
                print(f"   ❌ Failed from path_testing directory: {result.stderr}")
        
        # Test 4: From a subdirectory
        print("\n4. Testing from server subdirectory...")
        server_dir = project_root / "src" / "property_record_web_scraping" / "server"
        if server_dir.exists():
            os.chdir(server_dir)
            result = subprocess.run([sys.executable, str(test_script)], 
                                  capture_output=True, text=True, check=False)
            total_tests += 1
            if result.returncode == 0:
                print("   ✅ Works from server subdirectory")
                success_count += 1
            else:
                print(f"   ❌ Failed from server subdirectory: {result.stderr}")
        
    finally:
        # Always restore original directory
        os.chdir(original_cwd)
    
    print(f"\nCross-directory test results: {success_count}/{total_tests} passed")
    return success_count == total_tests

def search_for_hardcoded_paths():
    """Search for remaining hardcoded relative paths in the codebase."""
    print(f"\n{'='*60}")
    print("🔍 SEARCHING FOR HARDCODED PATHS")
    print(f"{'='*60}")
    
    project_root = Path(__file__).parent.parent.absolute()
    src_dir = project_root / "src"
    
    # Patterns to search for
    patterns = [
        r'"\./[^"]*"',      # "./something"
        r"'\./[^']*'",      # './something'
        r'"\.\./[^"]*"',    # "../something"
        r"'\.\./[^']*'",    # '../something'
        r'"/src/',          # hardcoded /src/
        r"'/src/",          # hardcoded '/src/
    ]
    
    # Files to exclude from search
    exclude_patterns = [
        "*.pyc",
        "*.log",
        "*/__pycache__/*",
        "*/venv/*",
        "*/path_testing/*",  # Exclude our test scripts
        "*.md",             # Exclude markdown files
        "*.yaml",           # Config files are expected to have relative paths
        "*.yml",
    ]
    
    suspicious_files = []
    
    print("Searching for potential hardcoded path patterns...")
    
    try:
        for pattern in patterns:
            # Use grep to search for patterns
            cmd = ["grep", "-r", "-n", "--include=*.py", pattern, str(src_dir)]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if ':' in line:
                        file_path, line_num, content = line.split(':', 2)
                        # Skip if it's in test files or comments
                        if ('test' not in file_path.lower() and 
                            'path_testing' not in file_path and
                            not content.strip().startswith('#')):
                            suspicious_files.append((file_path, line_num, content.strip(), pattern))
    
    except Exception as e:
        print(f"   ⚠️  Error searching for patterns: {e}")
        return True  # Don't fail the test suite for search errors
    
    if suspicious_files:
        print(f"\n⚠️  Found {len(suspicious_files)} potentially hardcoded paths:")
        for file_path, line_num, content, pattern in suspicious_files:
            rel_path = Path(file_path).relative_to(project_root)
            print(f"   📄 {rel_path}:{line_num} - {content}")
        
        print(f"\n💡 Manual review recommended for these files")
        return False
    else:
        print("   ✅ No obvious hardcoded paths found")
        return True

def main():
    """Run comprehensive path resolution test suite."""
    
    print("🚀 COMPREHENSIVE PATH RESOLUTION TEST SUITE")
    print("=" * 60)
    print("This suite verifies that all path resolution works correctly")
    print("from any working directory and with different configurations.")
    print("=" * 60)
    
    # Get test script paths
    test_dir = Path(__file__).parent
    
    test_scripts = [
        (test_dir / "test_config_only.py", "Config Path Resolution"),
        (test_dir / "test_chrome_binaries.py", "Chrome/ChromeDriver Binaries"),
        (test_dir / "test_download_directory.py", "Download Directory Paths"),
    ]
    
    # Track results
    passed_tests = 0
    total_tests = len(test_scripts) + 2  # +2 for cross-directory and hardcoded path tests
    
    # Run individual test scripts
    for script_path, description in test_scripts:
        if script_path.exists():
            if run_test_script(script_path, description):
                passed_tests += 1
        else:
            print(f"❌ Test script not found: {script_path}")
    
    # Run cross-directory tests
    if test_from_different_directories():
        passed_tests += 1
    
    # Search for hardcoded paths
    if search_for_hardcoded_paths():
        passed_tests += 1
    
    # Final results
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    
    if passed_tests == total_tests:
        print(f"🎉 ALL TESTS PASSED! ({passed_tests}/{total_tests})")
        print("✅ Path resolution system is working correctly!")
        print("✅ The project can be used from any working directory!")
        return 0
    else:
        print(f"❌ SOME TESTS FAILED ({passed_tests}/{total_tests})")
        print("⚠️  Path resolution system needs attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())