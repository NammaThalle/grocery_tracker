"""
Base service interfaces for the Grocery Bot system.
"""
import logging
from abc import ABC, abstractmethod
from typing import Protocol, List
from PIL import Image

logger = logging.getLogger(__name__)

class AIService(Protocol):
    """Protocol for AI service implementations"""
    
    def call(self, prompt: str) -> str:
        """Call AI service with text prompt"""
        ...
    
    def call_with_image(self, prompt: str, image: Image.Image) -> str:
        """Call AI service with prompt and image"""
        ...

class DataStorageService(Protocol):
    """Protocol for data storage service implementations"""
    
    async def save_items(self, items: List) -> str:
        """Save items to storage"""
        ...
    
    async def create_headers_if_needed(self) -> None:
        """Create headers if they don't exist"""
        ...

class BaseService(ABC):
    """Abstract base class for all services"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        logger.info(f"✅ {service_name} initialized")
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the service is healthy"""
        pass