import logging


def setup_logger(src: str, pth: str, level=logging.INFO):
    """
    Create logger to log system message.
    
    Args:
        src: logger name.
        pth: path to log file.
    """
    handler = logging.FileHandler(pth)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(src)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    return logger
