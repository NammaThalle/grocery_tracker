import logging
import os
from singleton_decorator import singleton

@singleton
class Logger:
    def __init__(self):
        """Initialize the singleton logger instance."""
        self.logger = logging.getLogger("GlobalLogger")

        # Define log format
        FORMAT = logging.Formatter(fmt="%(asctime)s - %(levelname).3s - %(filename)s:%(lineno).3d - %(message)s", 
                                   datefmt="%Y-%m-%d %H:%M:%S")

        # Configure logging only once
        logging.basicConfig(level=logging.INFO)

        def log_filter(record):
            """Filter out logs containing 'AFC'."""
            return "AFC" not in record.getMessage()

        # Apply the filter
        for handler in logging.getLogger().handlers:
            handler.addFilter(log_filter)
            handler.setFormatter(FORMAT)
        
    def get_logger(self):
        """Return the logger instance."""
        return self.logger

# Create a global logger instance
logger = Logger().get_logger()
