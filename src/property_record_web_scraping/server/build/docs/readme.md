# Build Directory

## Overview
The `Build` directory is responsible for managing the setup and installation of essential tools and dependencies required for the project. This includes downloading, configuring, and preparing the Chrome browser and ChromeDriver binaries, as well as ensuring that the necessary system dependencies are installed. The scripts and files in this directory automate the setup process, making it easier for developers to get started with the project.

---

## Directory Structure
The `Build` directory contains the following files and subdirectories:

---

## File Descriptions

### 1. `build-chrome-utils.sh`
- **Purpose**: Automates the setup of Chrome and ChromeDriver binaries, along with their dependencies.
- **Key Features**:
  - Downloads the latest Chrome and ChromeDriver binaries using metadata from Google's API.
  - Installs required system dependencies (e.g., `wget`, `curl`, `unzip`, `jq`, and libraries for Chrome).
  - Configures the binaries for use in the project.
  - Cleans up redundant or outdated binaries to ensure a clean setup.
- **Use Case**: This script is executed to prepare the environment for web scraping tasks that rely on Chrome and ChromeDriver.

---

### 2. `bin/`
- **Purpose**: Stores the downloaded binaries for Chrome and ChromeDriver.
- **Key Features**:
  - Contains the Chrome binary (`chrome-linux64`) and ChromeDriver binary (`chromedriver-linux64`).
  - Ensures that the binaries are organized and accessible for the project.
- **Use Case**: The `bin/` directory is used by the `Driver` class in the `ScraperUtils` module to initialize the Chrome WebDriver.

---

### 3. `docs/`
- **Purpose**: Contains documentation related to the `Build` directory.
- **Details**:
  - May include markdown files, diagrams, or other resources explaining the setup process.
  - Helps developers understand how to use the `build-chrome-utils.sh` script and troubleshoot issues.

---

### 4. `src/`
- **Purpose**: Contains additional scripts or source files required for building utilities.
- **Details**:
  - This directory may include helper scripts or configuration files used during the build process.
  - Currently, its contents are not explicitly described but may be expanded in the future.

---

## Deliverables
The `Build` directory provides the following deliverables:
1. **Automated Setup Script**: The `build-chrome-utils.sh` script simplifies the process of setting up Chrome and ChromeDriver for the project.
2. **Binaries for Chrome and ChromeDriver**: The `bin/` directory contains the necessary binaries for running web scraping tasks.
3. **Documentation**: The `docs/` folder provides resources to help developers understand and use the build utilities effectively.

---

## Use Cases

### 1. **Setting Up Chrome and ChromeDriver**
- The `build-chrome-utils.sh` script is used to download and configure the latest versions of Chrome and ChromeDriver.
- Example:
  ```bash
  # Navigate to the Build directory
  cd Build

  # Run the setup script
  ./build-chrome-utils.sh