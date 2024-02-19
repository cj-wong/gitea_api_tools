import logging
import logging.handlers
from pathlib import Path


def create_logger(log_name: str, cache_dir: Path) -> logging.Logger:
    """Create logger into the cache directory.

    Args:
        cache_dir: the path to the cache directory for logging

    Returns:
        logging.Logger: the logger

    """
    log_file = cache_dir / f'{log_name}.log'
    max_log_size = 40960
    max_log_files = 5

    logger = logging.getLogger(log_name)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_log_size,
        backupCount=max_log_files,
        )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        logging.Formatter(
            '%(levelname)s - %(message)s'
            )
        )

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
