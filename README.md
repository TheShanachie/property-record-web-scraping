# Property Record Web Scraping

A Flask-based web scraping API for extracting property records from public databases. This proof-of-concept demonstrates asynchronous task management, driver pooling, and structured data extraction using Selenium WebDriver and simulated chrome. This project started as a simple, less flexible web scraping utility as part of a much larger project, but it became something more. It is not intended for professional, commercial, or any real use. This program is build to scrape the existing property database site for Northhampton County, PA. If you use this package, it is recommended that you view the system requirements and install the package in a virtual environment.


## Quick Links
**TestPypi**: [Link to TestPyPi Page](https://test.pypi.org/project/property-record-web-scraping/0.0.15/)

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

*To be detailed...*

## Project Structure

*To be detailed...*
