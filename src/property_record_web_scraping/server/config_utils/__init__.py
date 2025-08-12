from property_record_web_scraping.server.config_utils.Config import Config

## Initialize config with correct path - singleton pattern ensures this only happens once
Config.initialize()  # Uses default config directory from get_config_dir()

## Export the class to be used.
__all__ = ['Config']