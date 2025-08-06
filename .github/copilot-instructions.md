# AI Coding Agent Instructions

## Project Overview
This is a **property record web scraping API** built with Flask that provides RESTful endpoints for scraping property records. The system uses Selenium WebDriver with Chrome for web scraping, implements task-based asynchronous processing, and provides comprehensive logging and configuration management.

## Architecture & Key Components

### Core Application Structure
- **Entry Point**: `src/app.py` imports and runs `server.app`
- **Server Module**: `src/server/` contains all core functionality
- **Configuration**: YAML-based config in `src/server/config/` managed by singleton `Config` class
- **Models**: Pydantic models in `src/server/models/` for input/output validation and metadata
- **Web Scraping**: `src/server/web_scraping_utils/scraper_utils/` contains Chrome automation logic

### Task Management Architecture
The system implements **asynchronous task processing** with these key components:
- **TaskManager** (`task_manager.py`): Manages concurrent tasks using ThreadPoolExecutor
- **DriverPool** (`driver_pool.py`): Thread-safe pool of Selenium WebDriver instances  
- **EventsHandler** (`events.py`): Coordinates task execution and cleanup
- **Routes** (`routes.py`): Flask Blueprint with decorated endpoints for logging

### Critical Patterns

#### Python Virtual Environment, Dependencies, and Python Version
This project uses a **Python virtual environment** to manage dependencies. Ensure you have Python 3.10 or higher installed. The dependencies are managed via `requirements.txt`. This file should NOT be modified directly, without robust review.

#### Configuration Management
```python
# Config is a singleton initialized early in server/__init__.py
from server.config_utils import Config
config = Config.get_config("flask_app")  # Gets from flask_app.yaml
```
All config files are in `src/server/config/` and use relative path resolution starting with `./src/server/`.

#### Model Structure
Models follow a specific inheritance pattern:
- **SafeErrorMixin**: Provides error handling fields (`error`, `error_message`)
- **Metadata**: Task metadata with status, timestamps, validation, error details, IO, etc.
- **ActionInput/ActionOutput**: Request/response models with Pydantic validation

#### Task ID Generation
Task IDs are generated in `Metadata` model using `uuid4().hex` with field validators. Be aware of potential ID consistency issues between server and test models.

#### Logging System
Four specialized loggers configured via YAML:
- `web_scraping_core_logger`: Core scraping operations
- `flask_app_interactions_logger`: API request/response logging  
- `event_handling_operations_logger`: Task management events
- `resource_management_logger`: Driver pool and resource management

## Development Workflows

### Running the Server
```bash
cd src/
python3 app.py  # Runs on localhost:5000 by default
```

### Running Tests
```bash
cd src/
python3 run_tests.py  # Starts server, runs tests, stops server
```
The test runner uses `os.fork()` to spawn server process and `SIGKILL` for cleanup.

### Setting Up Chrome Dependencies  
```bash
cd src/server/build/
./build.sh  # Downloads Chrome 138.0.7201.0 and ChromeDriver to bin/
```

### Testing Patterns
- **Base Test Class**: `test/tests/base_test.py` provides model validation helpers
- **API Client**: `test/test_utilities/api_client.py` with Pydantic response validation
- **Test Structure**: All tests inherit from `BaseAPITest` and use `self.client.submit_scrape_job()` among other methods for API interaction.

## Project-Specific Conventions

### Import Patterns
```python
# Server modules use relative imports
from server.models import ActionInput, ActionOutput
from server.config_utils import Config
from server.logging_utils import event_handling_operations_logger

# Tests use absolute imports from server
from server.models import ActionInput, ActionOutput  
```

### Error Handling
- All models inherit from `SafeErrorMixin` for consistent error structure
- Routes use `@log_flask_endpoint_io()` decorator for request/response logging
- TaskManager implements cleanup threads for failed/completed tasks

### Path Resolution
The `Config` class resolves relative paths using project root detection:
```python
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
```

### API Endpoints
- Base URL: `/api/v1`
- Key endpoints: `/scrape`, `/task/{id}/status`, `/task/{id}/result`, `/tasks`, `/health`
- All responses follow `ActionOutput` model structure.

## Critical Integration Points

### Driver Pool Management
- Max drivers configurable via `events_handler_init.yaml`
- Thread-safe borrowing/returning of WebDriver instances
- Automatic cleanup of inactive drivers

### Task State Management  
- Tasks stored in `TaskManager._tasks` dict with `Metadata` objects
- Futures tracked in `TaskManager._futures` with threading events
- Status transitions: CREATED → PENDING → RUNNING → COMPLETED/FAILED/STOPPING/CANCELED

### Configuration Loading
- Config automatically loaded from `src/server/config/` on import
- Supports single files, file lists, or directories
- Path resolution for Chrome binary locations

## Common Pitfalls
- **Model Consistency**: Ensure server and test `Metadata` models have identical field definitions
- **Task ID Uniqueness**: Verify ID generation consistency across model validation
- **Resource Cleanup**: TaskManager and DriverPool require proper shutdown handling
- **Path Dependencies**: Chrome binary paths are resolved relative to project root

## Debugging Tips
- Check `src/server/logs/` for application logs
- Use `client.get_health()` to verify API connectivity  
- Examine task status progression via `/task/{id}/status` endpoint
- Monitor driver pool stats through `TaskManager.driver_pool_info()`
