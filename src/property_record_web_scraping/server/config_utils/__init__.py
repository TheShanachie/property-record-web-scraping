from server.config_utils.Config import Config
import os

## This should make sure the config details are initialized early.
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
config_source_dir = os.path.join(parent_dir, 'config')
Config.initialize(source=config_source_dir)

## Export the class to be used.
__all__ = ['Config']