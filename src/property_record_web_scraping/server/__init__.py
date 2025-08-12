"""
server

This package contains the main server logic, API routes, thread/driver pool managers,
and web scraping utilities for the application.
"""
# Import preliminary modules
import sys
import os
from pathlib import Path

# Set up import paths for server module resolution
server_dir = Path(__file__).parent.absolute()  # server/
property_dir = server_dir.parent.absolute()    # property_record_web_scraping/

# Add property_record_web_scraping directory to Python path so 'from server.' imports work
if str(property_dir) not in sys.path:
    sys.path.insert(0, str(property_dir))

# Set project root for consistent path resolution  
if 'PROJECT_ROOT' not in os.environ:
    # Check if we're in development (has src/ parent) or installed package
    if property_dir.parent.name == "src":
        # Development mode: src/property_record_web_scraping/
        src_dir = property_dir.parent.absolute()  # src/
        project_root = src_dir.parent.absolute()  # project root
    else:
        # Installed package mode: site-packages/property_record_web_scraping/
        project_root = property_dir.absolute()     # use package dir as project root
    
    os.environ['PROJECT_ROOT'] = str(project_root)

project_root = Path(os.environ['PROJECT_ROOT'])

# Build the project binaries if it is necessary.
from .build import install_chrome_and_driver_fixed_dirs

# Determine correct build directory based on installation context
# Check if we're in development by looking for pyproject.toml in project_root
if (project_root / "pyproject.toml").exists():
    # Development mode - has pyproject.toml file
    build_dir = project_root / "src" / "property_record_web_scraping" / "server" / "build" / "bin"
else:
    # Installed package mode - no pyproject.toml in package directory
    build_dir = project_root / "server" / "build" / "bin"

# Create build directory if it doesn't exist
build_dir.mkdir(parents=True, exist_ok=True)

install_chrome_and_driver_fixed_dirs(
    chrome_url="https://storage.googleapis.com/chrome-for-testing-public/138.0.7201.0/linux64/chrome-linux64.zip",
    driver_url="https://storage.googleapis.com/chrome-for-testing-public/138.0.7201.0/linux64/chromedriver-linux64.zip",
    build_dir=str(build_dir),
    check_exists=True,
    overwrite=True,
)
    
# Add the src directory to the system path for imports
src_dir = project_root / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))
    
# Import the main server application, create it, then expose it.
from server.app import _create_app
app = _create_app()

# Expose the app for use in other modules
__all__ = ['app']