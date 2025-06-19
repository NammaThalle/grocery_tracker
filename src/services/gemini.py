"""
Service for interacting with Gemini AI.
"""
import logging

from PIL import Image
from google import genai
from config import config, singleton
from .base import BaseService

logger = logging.getLogger(__name__)

@singleton
class GeminiService(BaseService):
    """Service for interacting with Gemini AI - Singleton to reuse client"""
    
    def __init__(self):
        super().__init__("Gemini AI Service")
        self.client = genai.Client(api_key=config.gemini_api_key)
    
    def call(self, prompt: str) -> str:
        """Call Gemini API with text prompt"""
        try:
            response = self.client.models.generate_content(
                model=config.gemini_model,
                contents=[prompt]
            )
            return response.text # type: ignore
        except Exception as e:
            logger.error(f"Error calling Gemini: {e}")
            return f"Error: {str(e)}"
    
    def call_with_image(self, prompt: str, image: Image.Image) -> str:
        """Call Gemini API with prompt and image"""
        try:
            response = self.client.models.generate_content(
                model=config.gemini_model,
                contents=[prompt, image]
            )
            return response.text # type: ignore
        except Exception as e:
            logger.error(f"Error calling Gemini with image: {e}")
            return f"Error: {str(e)}"
    
    async def health_check(self) -> bool:
        """Check if Gemini service is healthy"""
        try:
            test_response = self.call("Test")
            return not test_response.startswith("Error")
        except Exception as e:
            logger.error(f"Gemini health check failed: {e}")
            return False