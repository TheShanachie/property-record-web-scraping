from .Config import Config

## This should make sure the config details are initialized early.
Config() # The config details are initialized with default path values.

## Export the class to be used.
__all__ = ['Config']