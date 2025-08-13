# Path Resolution Fixes

## Goal
Make path resolution uniform between development and packaging by using package-relative paths.

## Tasks

- [x] Update YAML configs to use package-relative paths
- [x] Simplify Config.py path resolution logic  
- [x] Remove get_build_dir() complexity
- [x] Update path tests to match new behavior
- [x] Test changes in both development and package modes

## Implementation Steps

### 1. Update YAML configs to use package-relative paths
- Change `selenium_chrome.yaml` paths from `./src/property_record_web_scraping/server/...` to `./server/...`
- Update any other config files with similar paths

### 2. Simplify Config.py path resolution logic
- Modify `resolve_path()` to always resolve from package root
- Remove development vs package detection logic
- All `./` paths resolve from `get_package_root()`

### 3. Remove get_build_dir() complexity  
- Always return `get_package_root() / "server" / "build" / "bin"`
- Remove conditional logic based on pyproject.toml existence

### 4. Update path tests
- Modify test expectations to match package-relative behavior
- Update hardcoded test paths in path_testing directory

### 5. Test changes
- Verify development mode still works
- Test package installation and runtime
- Ensure all path resolution tests pass