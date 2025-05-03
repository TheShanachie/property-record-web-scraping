#!/usr/bin/bash

# Download directory
DOWNLOAD_DIR="./bin/"

# Change to download directory
pushd "$DOWNLOAD_DIR" || exit

# Update and install necessary packages
sudo apt update && sudo apt upgrade -y
sudo apt install wget curl unzip jq -y

# Remove redundant binaries
for dir in */; do
  if [[ "${dir}" == chrome* ]]; then
    echo "Removing directory: ${dir}"
    rm -rf "${dir}"
  fi
done

# Fetch metadata for the latest Chrome and ChromeDriver
meta_data=$(curl -s 'https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json')

# Download the latest Chrome binary
chrome_url=$(echo "$meta_data" | jq -r '.channels.Stable.downloads.chrome[0].url')
wget "$chrome_url" -O chrome-linux64.zip

# Install required dependencies
sudo apt install ca-certificates fonts-liberation \
    libappindicator3-1 libasound2 libatk-bridge2.0-0 libatk1.0-0 libc6 \
    libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgbm1 \
    libgcc1 libglib2.0-0 libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 \
    libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 \
    libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 \
    libxrandr2 libxrender1 libxss1 libxtst6 lsb-release wget xdg-utils -y

# Unzip the Chrome binary
unzip chrome-linux64.zip

# Download the latest ChromeDriver binary
chromedriver_url=$(echo "$meta_data" | jq -r '.channels.Stable.downloads.chromedriver[0].url')
wget "$chromedriver_url" -O chromedriver-linux64.zip

# Unzip the ChromeDriver binary
unzip chromedriver-linux64.zip

# Clean up downloaded zip files
rm chrome-linux64.zip chromedriver-linux64.zip

# Change back to the original directory
popd || exit