from setuptools import setup
from setuptools.command.install import install
import os
import runpy

class InstallChromeCommand(install):
    """Custom install command to fetch Chrome and ChromeDriver."""
    def run(self):
        # Run standard install first
        super().run()

        # Run your installer script
        # During installation, use simple relative path from setup.py location
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "property_record_web_scraping", "server", "build.py")

        print("🔧 Installing Chrome and ChromeDriver...")
        runpy.run_path(script_path, run_name="__main__")
        print("✅ Chrome installation complete.")

setup(
    cmdclass={"install": InstallChromeCommand}

)