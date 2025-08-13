# Use centralized Config for path setup
from property_record_web_scraping.server.config_utils import Config
Config.setup_python_path()

# Import the server once the paths are set up
import property_record_web_scraping.server as server

def main():
    server.build(run_immediately=True)

if __name__ == '__main__':
    main()