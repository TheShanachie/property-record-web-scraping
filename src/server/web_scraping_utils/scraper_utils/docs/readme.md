# ScraperUtils Directory

## Overview
The `ScraperUtils` directory is the core module for handling web scraping operations in the project. It provides utilities, classes, and functions to interact with web pages, extract data, and manage the scraping workflow. This directory encapsulates all the logic required for web scraping, including browser automation, element interaction, data parsing, and error handling.

The utilities in this directory are designed to work seamlessly with other modules, such as `LoggingUtils` for logging and `ConfigUtils` for configuration management. Together, they enable efficient and reliable web scraping.

---

## Directory Structure
The `ScraperUtils` directory contains the following files and subdirectories:

---

## File Descriptions

### 1. `__init__.py`
- **Purpose**: Marks the `ScraperUtils` directory as a Python package, allowing its modules to be imported elsewhere in the project.
- **Details**: This file may include package-level imports or initialization logic.

---

### 2. `Driver.py`
- **Purpose**: Provides the `Driver` class, which manages the web scraping workflow.
- **Key Features**:
  - Initializes and configures the Selenium WebDriver.
  - Handles browser automation, including navigation and interaction with web pages.
  - Integrates logging for tracking events and errors during scraping.
  - Provides methods for passing disclaimers, submitting search queries, and collecting data.
- **Use Case**: Acts as the central controller for web scraping tasks.

---

### 3. `GetElement.py`
- **Purpose**: Contains utility functions for interacting with web elements.
- **Key Features**:
  - Functions to locate and interact with web elements using Selenium.
  - Includes error handling for missing or inaccessible elements.
  - Provides helper functions for waiting for elements or pages to load.
- **Use Case**: Used to simplify and standardize interactions with web elements during scraping.

---

### 4. `RecordScraper.py`
- **Purpose**: Provides functions for parsing and extracting data from individual records.
- **Key Features**:
  - Functions to parse property records, including headings, details, and images.
  - Handles navigation between records and pages.
  - Includes error handling for incomplete or missing data.
- **Use Case**: Used to extract structured data from web pages, such as property details or owner information.

---

### 5. `RecordSearch.py`
- **Purpose**: Provides functions for submitting and managing search queries.
- **Key Features**:
  - Functions to submit address-based searches.
  - Handles form interactions and search result navigation.
  - Includes error handling for invalid or incomplete search queries.
- **Use Case**: Used to initiate and manage search operations on the target website.

---

### 6. `__pycache__/`
- **Purpose**: Stores compiled Python files (`.pyc`) for performance optimization.
- **Details**: This directory is automatically generated by Python and does not require manual modification.

---

### 7. `docs/`
- **Purpose**: Contains documentation related to the `ScraperUtils` module.
- **Details**:
  - May include markdown files, diagrams, or other resources explaining the purpose and usage of the scraping utilities.
  - Helps developers understand how to use the module effectively.

---

## Deliverables
The `ScraperUtils` directory provides the following deliverables:
1. **Web Scraping Driver**: The `Driver.py` module provides a centralized class for managing the web scraping workflow.
2. **Element Interaction Utilities**: The `GetElement.py` module simplifies interactions with web elements.
3. **Data Extraction Functions**: The `RecordScraper.py` module provides functions for parsing and extracting structured data.
4. **Search Management Functions**: The `RecordSearch.py` module handles search queries and result navigation.
5. **Documentation**: The `docs/` folder provides resources to help developers understand and use the scraping utilities effectively.

---

## Use Cases

### 1. **Automating Web Scraping Tasks**
- The `Driver` class in `Driver.py` is used to automate web scraping tasks, such as navigating to a website, submitting search queries, and collecting data.
- Example:
  ```python
  from ScraperUtils.Driver import Driver

  driver = Driver()
  results = driver.address_search(address="Main St", pages=["Parcel", "Owner"], num_results=5)