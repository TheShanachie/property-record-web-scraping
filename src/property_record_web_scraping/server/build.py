import os
import sys
import stat
import shutil
import tempfile
import zipfile
import urllib.request
from property_record_web_scraping.server.config_utils import Config


def install_chrome_and_driver_fixed_dirs(
    chrome_url: str,
    driver_url: str,
    build_dir: str,
    check_exists: bool = True,
    overwrite: bool = False,
) -> dict:
    """
    Install Chrome and ChromeDriver into fixed subdirectories under build_dir.

    Args:
        chrome_url: Direct URL to Chrome zip.
        driver_url: Direct URL to ChromeDriver zip.
        build_dir: Base directory to install into.
        overwrite: If True, remove existing folders before installing.

    Returns:
        dict with paths to installed binaries.
    """
    # Make sure the build directory exists.
    assert os.path.isdir(build_dir), f"Build directory does not exist: {build_dir}"
    
    chrome_dir = os.path.join(build_dir, "chrome-linux64")
    driver_dir = os.path.join(build_dir, "chromedriver-linux64")

    if check_exists:
        if os.path.exists(chrome_dir) and os.path.exists(driver_dir):
            return {
                "chrome": _locate_binary(chrome_dir, ["chrome", "chrome.exe"]),
                "chromedriver": _locate_binary(driver_dir, ["chromedriver", "chromedriver.exe"]),
            }

    if overwrite:
        for d in (chrome_dir, driver_dir):
            if os.path.exists(d):
                shutil.rmtree(d)

    os.makedirs(chrome_dir, exist_ok=True)
    os.makedirs(driver_dir, exist_ok=True)

    _download_and_extract(chrome_url, chrome_dir)
    _download_and_extract(driver_url, driver_dir)

    chrome_exec = _locate_binary(chrome_dir, ["chrome", "chrome.exe"])
    driver_exec = _locate_binary(driver_dir, ["chromedriver", "chromedriver.exe"])

    _ensure_executable(chrome_exec)
    _ensure_executable(driver_exec)

    return {
        "chrome": chrome_exec,
        "chromedriver": driver_exec,
    }


def _download_and_extract(url: str, dest_dir: str) -> None:
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".zip")
    os.close(tmp_fd)
    try:
        with urllib.request.urlopen(url) as resp, open(tmp_path, "wb") as f:
            shutil.copyfileobj(resp, f)
        with zipfile.ZipFile(tmp_path) as z:
            z.extractall(dest_dir)
    finally:
        os.remove(tmp_path)

def _locate_binary(root: str, names: list) -> str:
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if f in names:
                return os.path.join(dirpath, f)
    raise RuntimeError(f"Binary not found in {root}")


def _ensure_executable(path: str) -> None:
    if not sys.platform.startswith("win"):
        st = os.stat(path)
        os.chmod(path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

def is_built(chrome_dir: str, driver_dir: str) -> bool:
    """
    Return whether the chrome and chromedriver binaries are installed.
    """
    chrome_installed = False
    driver_installed = False

    try:
        chrome_installed = _locate_binary(chrome_dir, ["chrome", "chrome.exe"]) is not None
        driver_installed = _locate_binary(driver_dir, ["chromedriver", "chromedriver.exe"]) is not None
    except RuntimeError:
        pass

    return chrome_installed and driver_installed

def build() -> None:
    """
    If the dependencies aren't built, build them.
    """
    build_dir = Config.get_build_dir()
    if not is_built(
        chrome_dir=os.path.join(build_dir, "chrome-linux64"),
        driver_dir=os.path.join(build_dir, "chromedriver-linux64"),
    ):
        install_chrome_and_driver_fixed_dirs(
            chrome_url="https://storage.googleapis.com/chrome-for-testing-public/138.0.7201.0/linux64/chrome-linux64.zip",
            driver_url="https://storage.googleapis.com/chrome-for-testing-public/138.0.7201.0/linux64/chromedriver-linux64.zip",
            build_dir=build_dir,
            check_exists=True,
            overwrite=True
        )


if __name__ == "__main__":
    # Build the project dependencies
    build()
