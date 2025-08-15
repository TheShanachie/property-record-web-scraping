import os
import sys
import stat
import shutil
import tempfile
import zipfile
import urllib.request
from property_record_web_scraping.server.config_utils import Config


def check_chrome_system_dependencies() -> None:
    """
    Checks for required system libraries for Chrome to run.
    Prints missing libraries and suggests installation commands.
    """
    import subprocess

    # List of required .so files for Chrome (Ubuntu/Debian)
    required_libs = [
        "libatk-1.0.so.0",
        "libgtk-3.so.0",
        "libasound.so.2",
        "libnss3.so",
        "libx11-xcb.so.1",
        "libxcomposite.so.1",
        "libxdamage.so.1",
        "libxrandr.so.2",
        "libgbm.so.1",
        "libpango-1.0.so.0",
        "libpangocairo-1.0.so.0",
        "libxshmfence.so.1",
        "libxss.so.1",
        "libxtst.so.6",
        "libappindicator3.so.1",
        "libcairo.so.2",
        "libcups.so.2",
        "libdrm.so.2",
        "libexpat.so.1",
        "libfontconfig.so.1",
        "libfreetype.so.6",
        "libglib-2.0.so.0",
        "libgdk_pixbuf-2.0.so.0",
        "libharfbuzz.so.0",
        "libjpeg.so.8",
        "libpng16.so.16",
        "libwebp.so.7",
        "libX11.so.6",
        "libXcomposite.so.1",
        "libXdamage.so.1",
        "libXext.so.6",
        "libXfixes.so.3",
        "libXrandr.so.2",
        "libXrender.so.1",
        "libXtst.so.6",
    ]

    missing = []
    try:
        result = subprocess.run(["ldconfig", "-p"], capture_output=True, text=True)
        libs_available = result.stdout
        for lib in required_libs:
            if lib not in libs_available:
                missing.append(lib)
    except Exception as e:
        print("Could not check system libraries:", e)
        return

    if missing:
        print("\n[!] The following Chrome dependencies are missing on your system:")
        for lib in missing:
            print("   ", lib)
        print("\nTo install most of these on Ubuntu/Debian, run:")
        print("   sudo apt-get update")
        print("   sudo apt-get install -y libatk1.0-0t64 libgtk-3-0t64 libasound2t64 libnss3 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libpango-1.0-0 libpangocairo-1.0-0 libxshmfence1 libxss1 libxtst6 fonts-liberation libappindicator3-1 libcairo2 libcups2 libdrm2 libexpat1 libfontconfig1 libfreetype6 libglib2.0-0 libgdk-pixbuf2.0-0 libharfbuzz0b libjpeg8 libpng16-16 libwebp7 libxext6 libxfixes3 libxrender1")
        print("\nIf you do not have root access, review privileges.")
    else:
        print("[✓] All required Chrome system libraries are installed.")


# def install_chrome_and_driver_fixed_dirs(
#     chrome_url: str,
#     driver_url: str,
#     build_dir: str,
#     check_exists: bool = True,
#     overwrite: bool = False,
# ) -> dict:
#     """
#     Install Chrome and ChromeDriver into fixed subdirectories under build_dir.

#     Args:
#         chrome_url: Direct URL to Chrome zip.
#         driver_url: Direct URL to ChromeDriver zip.
#         build_dir: Base directory to install into.
#         overwrite: If True, remove existing folders before installing.

#     Returns:
#         dict with paths to installed binaries.
#     """
#     # Make sure the build directory exists.
#     assert os.path.isdir(build_dir), f"Build directory does not exist: {build_dir}"

#     chrome_dir = os.path.join(build_dir, "chrome-linux64")
#     driver_dir = os.path.join(build_dir, "chromedriver-linux64")

#     if check_exists:
#         if os.path.exists(chrome_dir) and os.path.exists(driver_dir):
#             return {
#                 "chrome": _locate_binary(chrome_dir, ["chrome", "chrome.exe"]),
#                 "chromedriver": _locate_binary(driver_dir, ["chromedriver", "chromedriver.exe"]),
#             }

#     if overwrite:
#         for d in (chrome_dir, driver_dir):
#             if os.path.exists(d):
#                 shutil.rmtree(d)

#     os.makedirs(chrome_dir, exist_ok=True)
#     os.makedirs(driver_dir, exist_ok=True)

#     _download_and_extract(chrome_url, chrome_dir)
#     _download_and_extract(driver_url, driver_dir)

#     chrome_exec = _locate_binary(chrome_dir, ["chrome", "chrome.exe"])
#     driver_exec = _locate_binary(driver_dir, ["chromedriver", "chromedriver.exe"])

#     _ensure_executable(chrome_exec)
#     _ensure_executable(driver_exec)

#     return {
#         "chrome": chrome_exec,
#         "chromedriver": driver_exec,
#     }


# def _download_and_extract(url: str, dest_dir: str) -> None:
#     tmp_fd, tmp_path = tempfile.mkstemp(suffix=".zip")
#     os.close(tmp_fd)
#     try:
#         with urllib.request.urlopen(url) as resp, open(tmp_path, "wb") as f:
#             shutil.copyfileobj(resp, f)
#         with zipfile.ZipFile(tmp_path) as z:
#             z.extractall(dest_dir)
#     finally:
#         os.remove(tmp_path)

# def _download_and_extract(url: str, dest_dir: str) -> None:

#     tmp_fd, tmp_path = tempfile.mkstemp(suffix=".zip")
#     os.close(tmp_fd)
#     try:
#         with urllib.request.urlopen(url) as resp, open(tmp_path, "wb") as f:
#             shutil.copyfileobj(resp, f)
#         with zipfile.ZipFile(tmp_path) as z:
#             # Find the top-level directory in the zip
#             top_level = z.namelist()[0].split('/')[0]
#             for member in z.namelist():
#                 # Only extract files inside the top-level directory
#                 if member.startswith(top_level + '/') and not member.endswith('/'):
#                     # Remove the top-level directory from the path
#                     target = member[len(top_level) + 1 :]
#                     target_path = os.path.join(dest_dir, target)
#                     os.makedirs(os.path.dirname(target_path), exist_ok=True)
#                     with z.open(member) as source, open(target_path, "wb") as target_file:
#                         shutil.copyfileobj(source, target_file)
#     finally:
#         os.remove(tmp_path)

def _locate_binary(root: str, names: list) -> str:
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if f in names:
                return os.path.join(dirpath, f)
    raise RuntimeError(f"Binary not found in {root}")


def _ensure_all_executable(path: str) -> None:
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            full_path = os.path.join(dirpath, f)
            if not sys.platform.startswith("win"):
                st = os.stat(full_path)
                os.chmod(full_path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


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

# def build_binaries() -> None:
#     """
#     If the dependencies aren't built, build them.
#     """
#     build_dir = Config.get_build_dir()
#     check_chrome_system_dependencies()
#     if not is_built(
#         chrome_dir=os.path.join(build_dir, "chrome-linux64"),
#         driver_dir=os.path.join(build_dir, "chromedriver-linux64"),
#     ):
#         install_chrome_and_driver_fixed_dirs(
#             chrome_url="https://storage.googleapis.com/chrome-for-testing-public/138.0.7201.0/linux64/chrome-linux64.zip",
#             driver_url="https://storage.googleapis.com/chrome-for-testing-public/138.0.7201.0/linux64/chromedriver-linux64.zip",
#             build_dir=build_dir,
#             check_exists=True,
#             overwrite=False
#         )


def build_binaries() -> None:
    """
    If the dependencies aren't built, build them.
    """
    build_dir = Config.get_build_dir()
    print(f"[INFO] Checking Chrome system dependencies...")
    check_chrome_system_dependencies()
    chrome_dir = os.path.join(build_dir, "chrome-linux64")
    driver_dir = os.path.join(build_dir, "chromedriver-linux64")
    print(f"[INFO] Checking if Chrome and ChromeDriver binaries are already installed...")
    if not is_built(chrome_dir=chrome_dir, driver_dir=driver_dir):
        print(f"[INFO] Chrome or ChromeDriver not found. Downloading and installing...")
        install_chrome_and_driver_fixed_dirs(
            chrome_url="https://storage.googleapis.com/chrome-for-testing-public/138.0.7201.0/linux64/chrome-linux64.zip",
            driver_url="https://storage.googleapis.com/chrome-for-testing-public/138.0.7201.0/linux64/chromedriver-linux64.zip",
            build_dir=build_dir, check_exists=True, overwrite=False)
        print(f"[SUCCESS] Chrome and ChromeDriver installed in {build_dir}.")
    else:
        print(f"[INFO] Chrome and ChromeDriver already installed in {build_dir}.")


def install_chrome_and_driver_fixed_dirs(
    chrome_url: str,
    driver_url: str,
    build_dir: str,
    check_exists: bool = True,
    overwrite: bool = False,
) -> dict:
    """
    Install Chrome and ChromeDriver into fixed subdirectories under build_dir.
    """
    print(f"[INFO] Preparing to install Chrome and ChromeDriver in {build_dir}...")
    os.makedirs(build_dir, exist_ok=True)

    chrome_dir = os.path.join(build_dir, "chrome-linux64")
    driver_dir = os.path.join(build_dir, "chromedriver-linux64")

    if check_exists:
        if os.path.exists(chrome_dir) and os.path.exists(driver_dir):
            print(f"[INFO] Chrome and ChromeDriver directories already exist. Skipping download.")
            return {
                "chrome": _locate_binary(chrome_dir, ["chrome", "chrome.exe"]),
                "chromedriver": _locate_binary(driver_dir, ["chromedriver", "chromedriver.exe"]),
            }

    if overwrite:
        for d in (chrome_dir, driver_dir):
            if os.path.exists(d):
                print(f"[INFO] Removing existing directory: {d}")
                shutil.rmtree(d)

    os.makedirs(chrome_dir, exist_ok=True)
    os.makedirs(driver_dir, exist_ok=True)

    print(f"[INFO] Downloading and extracting Chrome from {chrome_url}...")
    _download_and_extract(chrome_url, chrome_dir)
    print(f"[INFO] Downloading and extracting ChromeDriver from {driver_url}...")
    _download_and_extract(driver_url, driver_dir)

    chrome_exec = _locate_binary(chrome_dir, ["chrome", "chrome.exe"])
    driver_exec = _locate_binary(driver_dir, ["chromedriver", "chromedriver.exe"])

    print(f"[INFO] Ensuring Chrome binary is executable: {chrome_exec}")
    _ensure_all_executable(chrome_dir)
    print(f"[INFO] Ensuring ChromeDriver binary is executable: {driver_exec}")
    _ensure_all_executable(driver_dir)

    return {
        "chrome": chrome_exec,
        "chromedriver": driver_exec,
    }


def _download_and_extract(url: str, dest_dir: str) -> None:
    print(f"[INFO] Downloading zip from {url}...")
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".zip")
    os.close(tmp_fd)
    try:
        with urllib.request.urlopen(url) as resp, open(tmp_path, "wb") as f:
            shutil.copyfileobj(resp, f)
        print(f"[INFO] Extracting zip to {dest_dir}...")
        with zipfile.ZipFile(tmp_path) as z:
            top_level = z.namelist()[0].split('/')[0]
            for member in z.namelist():
                if member.startswith(top_level + '/') and not member.endswith('/'):
                    target = member[len(top_level) + 1:]
                    target_path = os.path.join(dest_dir, target)
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with z.open(member) as source, open(target_path, "wb") as target_file:
                        shutil.copyfileobj(source, target_file)
        print(f"[SUCCESS] Extraction complete: {dest_dir}")
    finally:
        os.remove(tmp_path)
        print(f"[INFO] Removed temporary zip file.")


if __name__ == "__main__":
    # Build the project dependencies
    build_binaries()
