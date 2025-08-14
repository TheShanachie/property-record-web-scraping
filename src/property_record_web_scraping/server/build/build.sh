#!/usr/bin/env bash

# Releveant variables
DOWNLOAD_DIR=./bin
VERSION=138.0.7201.0
CHROME_DOWNLOAD_URL=https://storage.googleapis.com/chrome-for-testing-public/138.0.7201.0/linux64/chrome-linux64.zip
CHROMEDRIVER_DOWNLOAD_URL=https://storage.googleapis.com/chrome-for-testing-public/138.0.7201.0/linux64/chromedriver-linux64.zip

# Assuming the download directory exists
pushd $DOWNLOAD_DIR || exit 1

# DOWNLOAD CHROME
wget -q --show-progress $CHROME_DOWNLOAD_URL -O chrome-linux64.zip
if [ $? -ne 0 ]; then
    echo "Failed to download Chrome."
    exit 1
fi

# UNZIP CHROME
unzip -q chrome-linux64.zip
if [ $? -ne 0 ]; then
    echo "Failed to unzip Chrome."
    exit 1
fi

# REMOVE ZIP FILE
rm -f chrome-linux64.zip

# DOWNLOAD CHROMEDRIVER
wget -q --show-progress $CHROMEDRIVER_DOWNLOAD_URL -O chromedriver-linux64.zip
if [ $? -ne 0 ]; then
    echo "Failed to download ChromeDriver."
    exit 1
fi

# UNZIP CHROMEDRIVER
unzip -q chromedriver-linux64.zip
if [ $? -ne 0 ]; then
    echo "Failed to unzip ChromeDriver."
    exit 1
fi

# REMOVE ZIP FILE
rm -f chromedriver-linux64.zip

# SET EXECUTABLE PERMISSIONS
chmod +x chrome-linux64/chrome
chmod +x chromedriver-linux64/chromedriver

popd || exit 1

# PRINT SUCCESS MESSAGE
echo "Chrome and ChromeDriver have been successfully downloaded and set up in $DOWNLOAD_DIR."

# PRINT CHROME VERSION AND EXE PATH
echo "Downloaded versions:"
echo "  Chrome version: $VERSION"
echo "  Chromedriver version: $VERSION"
echo "Executable paths:"
echo "  Chrome executable path: $DOWNLOAD_DIR/chrome-linux64/chrome"
echo "  ChromeDriver executable path: $DOWNLOAD_DIR/chromedriver-linux64/chromedriver"