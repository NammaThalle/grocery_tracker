"""
Tool for processing receipt images using Gemini Vision.
"""
import json
import base64
import logging

from PIL import Image
from io import BytesIO
from .base import BaseTool
from src.services import GeminiService, PromptService
from src.models import JSONExtractor

logger = logging.getLogger(__name__)

class ProcessReceiptTool(BaseTool):
    """Tool for processing receipt images using Gemini Vision"""
    
    def __init__(self):
        super().__init__(
            name="process_receipt",
            description="Process receipt images to extract expense data"
        )
        self.gemini_service = GeminiService()
    
    async def execute(self, image_data: str = None, **kwargs) -> str: # type: ignore
        """Process receipt image and return structured data"""
        try:
            if not image_data:
                return "Error: No image data provided"
            
            # Decode image
            try:
                image_bytes = base64.b64decode(image_data)
                image = Image.open(BytesIO(image_bytes))
                logger.info(f"📸 Processing image of size: {image.size}")
            except Exception as e:
                return f"Error: Failed to decode image - {str(e)}"
            
            # Get prompt and process
            prompt = PromptService.get_receipt_processing_prompt()
            response = self.gemini_service.call_with_image(prompt, image)
            
            # Validate response
            if response.startswith("Error"):
                return response
            
            # Extract and validate JSON
            json_data = JSONExtractor.extract_json_from_text(response)
            if not json_data:
                return "Error: Failed to extract valid JSON from receipt"
            
            if not JSONExtractor.validate_expense_data(json_data):
                return "Error: Invalid expense data structure"
            
            logger.info(f"✅ Receipt processed: {len(json_data.get('items', []))} items found")
            return json.dumps(json_data)
            
        except Exception as e:
            logger.error(f"Receipt processing error: {e}")
            return f"Error processing receipt: {str(e)}"