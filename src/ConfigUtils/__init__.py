from .Config import Config

## This should make sure the config details are initialized early.
Config()

## Export the class to be used.
__all__ = ['Config']