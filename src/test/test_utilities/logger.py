import logging
import os
from pathlib import Path

def _create_test_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    """
    Create a test logger with the specified name and level.
    """
    filename = os.path.join(__file__, '..', '..', 'logs', f"{name}.log")

    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create console handler
    ch = logging.FileHandler(filename=filename, mode='a+')
    ch.setLevel(level)
    
    # Create formatter and add it to the handler
    fmt = '%(name)s | %(asctime)s | file="%(filename)s", func="%(funcName)s", line="%(lineno)d" | %(levelname)s: %(message)s'
    formatter = logging.Formatter(fmt)
    ch.setFormatter(formatter)
    
    # Add the handler to the logger
    logger.addHandler(ch)
    
    return logger

test_logger = _create_test_logger('test_logger')