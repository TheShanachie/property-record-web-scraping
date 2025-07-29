import logging

def _create_test_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    """
    Create a test logger with the specified name and level.
    """
    filename = f"./test/logs/{name}.log"
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create console handler
    ch = logging.FileHandler(filename=filename, mode='a+')
    ch.setLevel(level)
    
    # Create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s: %(message)s')
    ch.setFormatter(formatter)
    
    # Add the handler to the logger
    logger.addHandler(ch)
    
    return logger

test_logger = _create_test_logger('test_logger')