#!/usr/bin/env python3
"""
Test script to verify PhotoScraper download directory path resolution works correctly.
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path for absolute imports
script_dir = Path(__file__).parent.parent.absolute()
src_dir = script_dir / "src"
sys.path.insert(0, str(src_dir))

# Import Config directly
from property_record_web_scraping.server.config_utils.Config import Config

def test_download_directory_resolution():
    """Test that download directory paths resolve correctly."""
    
    print("🔍 Testing Download Directory Path Resolution")
    
    # Test 1: Check PhotoScraper hardcoded path
    print("\n1. Testing PhotoScraper hardcoded download directory...")
    test_path = "./Logs/TempEmpty"  # This is what PhotoScraper uses
    resolved_path = Config.resolve_path(test_path)
    print(f"   PhotoScraper path: '{test_path}' → '{resolved_path}'")
    
    if resolved_path.is_absolute():
        print("   ✅ PhotoScraper path resolved to absolute")
    else:
        print("   ❌ PhotoScraper path still relative")
        return False
    
    # Test 2: Check config download directory
    print("\n2. Testing config download directory...")
    Config.initialize()
    selenium_config = Config.get_config(['selenium_chrome'])
    config_download_dir = selenium_config.get('experimental-chrome-options', {}).get('download.default_directory')
    
    print(f"   Config download dir: {config_download_dir}")
    
    if config_download_dir and Path(config_download_dir).is_absolute():
        print("   ✅ Config download directory is absolute")
    else:
        print(f"   ❌ Config download directory issue: {config_download_dir}")
        return False
    
    # Test 3: Check if directories exist or can be created
    print("\n3. Testing directory existence/creation...")
    
    # Test PhotoScraper directory
    photoscraper_dir = Path(resolved_path)
    if photoscraper_dir.exists():
        print(f"   ✅ PhotoScraper directory exists: {photoscraper_dir}")
    else:
        print(f"   ⚠️  PhotoScraper directory doesn't exist (will be created): {photoscraper_dir}")
        try:
            photoscraper_dir.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ Successfully created PhotoScraper directory")
        except Exception as e:
            print(f"   ❌ Failed to create PhotoScraper directory: {e}")
            return False
    
    # Test config download directory
    config_dir = Path(config_download_dir)
    if config_dir.exists():
        print(f"   ✅ Config download directory exists: {config_dir}")
    else:
        print(f"   ⚠️  Config download directory doesn't exist (will be created): {config_dir}")
        try:
            config_dir.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ Successfully created config download directory")
        except Exception as e:
            print(f"   ❌ Failed to create config download directory: {e}")
            return False
    
    # Test 4: Verify they're accessible/writable
    print("\n4. Testing directory write access...")
    
    # Test PhotoScraper directory write access
    test_file1 = photoscraper_dir / "test_write.tmp"
    try:
        test_file1.write_text("test")
        test_file1.unlink()  # Clean up
        print(f"   ✅ PhotoScraper directory is writable")
    except Exception as e:
        print(f"   ❌ PhotoScraper directory not writable: {e}")
        return False
    
    # Test config directory write access
    test_file2 = config_dir / "test_write.tmp"
    try:
        test_file2.write_text("test")
        test_file2.unlink()  # Clean up
        print(f"   ✅ Config download directory is writable")
    except Exception as e:
        print(f"   ❌ Config download directory not writable: {e}")
        return False
    
    print("\n✅ All download directory tests passed!")
    return True

def main():
    """Run all download directory tests."""
    
    print("=" * 60)
    print("DOWNLOAD DIRECTORY PATH RESOLUTION VERIFICATION")
    print("=" * 60)
    
    success = test_download_directory_resolution()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED - Download directory paths work correctly!")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Download directory paths need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())