#!/bin/bash

set -e  # Exit immediately if any command fails

echo "[INFO] Removing build, dist, and egg-info directories..."
rm -rf build/ dist/ *.egg-info

echo "[INFO] Removing setuptools metadata from src (if present)..."
rm -rf src/*.egg-info

echo "[INFO] Removing .pyc and __pycache__ files..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

echo "[INFO] Build metadata and cache cleanup complete."

read -p "[PROMPT] Do you want to build the project now? [Y/n] " build_answer
case "$build_answer" in
    [Yy]* | "" )
        echo "[INFO] Building the project..."
        python3 -m build
        ;;
    * )
        echo "[INFO] Build cancelled by user."
        exit 0
        ;;
esac

echo "[INFO] Checking built package sizes..."
du -h dist/*

echo "[INFO] Checking for large files (>10MB) in built packages..."
LARGE_BUILT_FILES=$(find dist/ -type f -size +10M)
if [ -n "$LARGE_BUILT_FILES" ]; then
    echo "[ERROR] The following files in dist/ are over 10MB and may make your package too large for PyPI:"
    echo "$LARGE_BUILT_FILES"
    echo "[FAIL] Build contains files that are too large. Aborting upload."
    exit 1
else
    echo "[INFO] No oversized files detected in dist/. Proceeding to upload prompt."
fi

read -p "[PROMPT] Do you want to upload the package to TestPyPI? [Y/n] " answer
case "$answer" in
    [Yy]* | "" )
        echo "[INFO] Uploading package to TestPyPI with verbose output..."
        python3 -m twine upload --repository testpypi dist/* --verbose
        echo "[INFO] Done. Review the output above for any upload errors or warnings."
        ;;
    * )
        echo "[INFO] Upload cancelled by user."
        exit 0
        ;;
esac