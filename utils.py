import logging
import sys

def setup_logger(level=logging.INFO):
    """
    Sets up a standardized logger for the application.
    """
    logger = logging.getLogger("LoiteringApp")
    logger.setLevel(level)

    # Avoid adding duplicate handlers
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        # Create formatter and add it to the handler
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(handler)

    return logger

# Get a logger instance
logger = setup_logger()
