# Use centralized Config for path setup
from property_record_web_scraping.server.config_utils import Config
Config.setup_python_path()

import property_record_web_scraping.server as server

def main():
    server.app.run()

if __name__ == '__main__':
    main()