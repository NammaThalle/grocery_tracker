"""
Services package for the Grocery Bot system.

This package contains all external service integrations and business services.
Services are designed to be singleton where appropriate and follow dependency
injection patterns for better testability.
"""
from .base import BaseService, AIService, DataStorageService
from .gemini import GeminiService
from .google_sheets import GoogleSheetsService
from .prompts import PromptService
from .factory import ServiceFactory, service_factory

# Backward compatibility - maintain the same interface as before
# This allows existing code to work without changes
def get_gemini_service() -> GeminiService:
    """Get Gemini service instance"""
    return service_factory.get_service(GeminiService)

def get_sheets_service() -> GoogleSheetsService:
    """Get Google Sheets service instance"""
    return service_factory.get_service(GoogleSheetsService)

def get_prompt_service() -> PromptService:
    """Get Prompt service instance"""
    return service_factory.get_service(PromptService)

# Initialize services on import for backward compatibility
try:
    service_factory.initialize()
except Exception as e:
    import logging
    logging.getLogger(__name__).warning(f"Failed to auto-initialize services: {e}")

__all__ = [
    'BaseService',
    'AIService', 
    'DataStorageService',
    'GeminiService',
    'GoogleSheetsService', 
    'PromptService',
    'ServiceFactory',
    'service_factory',
    'get_gemini_service',
    'get_sheets_service',
    'get_prompt_service'
]