import os
import json
import base64

from utils.logging import logger
from singleton_decorator import singleton

@singleton
class Config:
    def __init__(self):
        """
        Initializes the Config singleton with environment variables.

        Args:
            env_file (str): The path to the .env file. Defaults to ".env".
        """
        self.config = dict(os.environ)

        # Decode the Google Service Info back to JSON format
        google_service_info = self.config.get("GOOGLE_SERVICE_INFO")
        google_service_info = base64.b64decode(google_service_info).decode("utf-8")
        self.config["GOOGLE_SERVICE_INFO"] = json.loads(google_service_info)
        
    def get(self, key, default=None):
        """
        Retrieves a configuration value by key.

        Args:
            key (str): The key of the configuration value.
            default: The default value to return if the key is not found.

        Returns:
            The configuration value or the default value if the key is not found.
        """
        return self.config.get(key, default)

    def __getitem__(self, key):
        """
        Allows accessing configuration values using dictionary-like syntax.

        Args:
            key (str): The key of the configuration value.

        Returns:
            The configuration value.

        Raises:
            KeyError: If the key is not found.
        """
        if key not in self.config:
            raise KeyError(f"Key '{key}' not found in configuration.")
        return self.config[key]

    def __contains__(self, key):
        """
        Checks if a key exists in the configuration.

        Args:
            key (str): The key to check.

        Returns:
            True if the key exists, False otherwise.
        """
        return key in self.config