# Property Record Web Scraping

A Flask-based web scraping API for extracting property records from public databases. This proof-of-concept demonstrates asynchronous task management, driver pooling, and structured data extraction using Selenium WebDriver and simulated chrome. This project started as a simple, less flexible web scraping utility as part of a much larger project, but it became something more. It is not intended for professional, commercial, or any real use. This program is build to scrape the existing property database site for Northhampton County, PA. If you use this package, it is recommended that you view the system requirements and install the package in a virtual environment.

## Technical Overview

- **Task Management**: ThreadPoolExecutor-based async processing with real-time status tracking
- **Driver Pool**: Managed Selenium WebDriver instances with automatic resource cleanup  
- **REST API**: Flask endpoints for task submission, monitoring, and result retrieval
- **Data Models**: Pydantic-validated structures for property records across multiple page types
- **Auto-Configuration**: Automatic Chrome/ChromeDriver setup with path resolution and dependency checking

## Dependencies

### Requirements
- **Python**: >=3.12
- **Gunicorn**: v23.0.0 (WSGI HTTP Server for production deployment)
- **Selenium**: v4.32.0
- **Chrome**: Compatible version automatically downloaded and managed
- **ChromeDriver**: Compatible version automatically downloaded and managed
- **Operating System**: Linux (POSIX) - Through the Ubuntu distro on Windows 11 WSL2
- **Packages**: Of course, there are many more packages listed in the `requirements.txt` file.

### System Requirements

**Required System Libraries** (for Chrome to run properly):
- libatk-1.0, libgtk-3, libasound2, libnss3
- libx11-xcb1, libxcomposite1, libxdamage1, libxrandr2
- libgbm1, libpango-1.0, libpangocairo-1.0
- libxshmfence1, libxss1, libxtst6, libappindicator3-1
- And other standard Linux graphics libraries

For Ubuntu/Debian systems, install with:
```bash
sudo apt-get update
sudo apt-get install -y libatk1.0-0 libgtk-3-0 libasound2 libnss3 libx11-xcb1 \
  libxcomposite1 libxdamage1 libxrandr2 libgbm1 libpango-1.0-0 libpangocairo-1.0-0 \
  libxshmfence1 libxss1 libxtst6 libappindicator3-1
```

## Installation

1. Clone/Fork the repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. The application will automatically download and configure Chrome/ChromeDriver on first run

## Usage

### Running the Application
The project provides convenient scripts defined in `pyproject.toml`:

**Start the web server:**
```bash
run-app
```

**Run the test suite:**
```bash
test-app
```

## Application Endpoints

### Task Management
- **POST** `/scrape` - Submit a new property scraping task
- **GET** `/task/<task_id>/status` - Get current status of a task
- **GET** `/task/<task_id>/result` - Retrieve results of a completed task
- **GET** `/task/<task_id>/wait` - Wait for task completion (not implemented)
- **POST** `/task/<task_id>/cancel` - Cancel a running task (not implemented)

### Task Monitoring
- **GET** `/tasks` - List all tasks in the system
- **GET** `/health` - Check system health and driver pool status

## Project Structure

The project follows a standard Python package structure with the main application code in `src/property_record_web_scraping/`. The `server/` directory contains the core Flask application, WebDriver management, and data models, while `test/` provides comprehensive testing utilities and test cases for API validation. There is always more to expand on.

```
property-record-web-scraping/
├── LICENSE
├── MANIFEST.in
├── README.md
├── build_and_upload.sh
├── pyproject.toml
├── requirements.txt
├── dist/                           # Distribution packages
├── path_testing/                   # Path resolution tests
│   ├── run_all_path_tests.py
│   ├── test_chrome_binaries.py
│   ├── test_config_only.py
│   ├── test_download_directory.py
│   ├── test_logging_directory.py
│   └── test_path_resolution.py
└── src/
   └── property_record_web_scraping/
       ├── __init__.py
       ├── app.py                  # Main application entry point
       ├── run_tests.py           # Test runner
       ├── server/                # Core server components
       │   ├── __init__.py
       │   ├── app.py             # Flask application
       │   ├── build.py           # Build utilities
       │   ├── driver_pool.py     # WebDriver pool management
       │   ├── events.py          # Event handling
       │   ├── routes.py          # API endpoints
       │   ├── server_cleanup.py  # Resource cleanup
       │   ├── task_manager.py    # Async task management
       │   ├── build/             # Build artifacts
       │   ├── config/            # YAML configuration files
       │   │   ├── address_utils.yaml
       │   │   ├── events_handler_init.yaml
       │   │   ├── flask_app.yaml
       │   │   ├── logging_utils.yaml
       │   │   └── selenium_chrome.yaml
       │   ├── config_utils/      # Configuration management
       │   │   ├── Config.py
       │   │   └── docs/
       │   ├── logging_utils/     # Logging infrastructure
       │   │   ├── loggers.py
       │   │   └── docs/
       │   ├── logs/              # Application logs
       │   ├── models/            # Data models and schemas
       │   │   ├── ActionErrorOutput.py
       │   │   ├── ActionInput.py
       │   │   ├── ActionOutput.py
       │   │   ├── Metadata.py
       │   │   ├── Record.py
       │   │   ├── SafeErrorMixin.py
       │   │   ├── SanitizeMixin.py
       │   │   └── recordpages/   # Property record page models
       │   │       ├── Commercial.py
       │   │       ├── Heading.py
       │   │       ├── Homestead.py
       │   │       ├── Land.py
       │   │       ├── MultiOwner.py
       │   │       ├── OutBuildings.py
       │   │       ├── Owner.py
       │   │       ├── Parcel.py
       │   │       ├── Photos.py
       │   │       ├── Residential.py
       │   │       ├── Sales.py
       │   │       └── Values.py
       │   └── web_scraping_utils/ # Web scraping utilities
       │       └── scraper_utils/
       │           ├── CheckSite.py
       │           ├── Driver.py
       │           ├── GetElement.py
       │           ├── PhotoScraper.py
       │           ├── RecordScraper.py
       │           ├── RecordSearch.py
       │           └── docs/
       └── test/                  # Test suite
           ├── logs/              # Test logs
           ├── test_utilities/    # Test helper utilities
           │   ├── api_client.py
           │   ├── logger.py
           │   └── record_examples.py
           └── tests/             # Test cases
               ├── base_test.py
               ├── test_cancel_task.py
               ├── test_health.py
               ├── test_invalid_submit_task.py
               ├── test_tasks.py
               ├── test_valid_submit.py
               └── test_valid_submit_pages.py
```
