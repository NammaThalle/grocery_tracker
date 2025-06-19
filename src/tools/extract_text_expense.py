"""
Tool for extracting expenses from text messages.
"""
import json
import logging

from .base import BaseTool
from src.services import GeminiService, PromptService
from src.models import JSONExtractor

logger = logging.getLogger(__name__)

class ExtractTextExpenseTool(BaseTool):
    """Tool for extracting expenses from text messages"""
    
    def __init__(self):
        super().__init__(
            name="extract_text_expense",
            description="Extract expense information from natural language text"
        )
        self.gemini_service = GeminiService()
    
    async def execute(self, text: str = None, **kwargs) -> str: # type: ignore
        """Extract expense data from text"""
        try:
            if not text:
                return "Error: No text provided"
            
            # Get prompt and process
            prompt = PromptService.get_text_expense_prompt(text)
            response = self.gemini_service.call(prompt)
            
            # Validate response
            if response.startswith("Error"):
                return response
            
            # Extract and validate JSON
            json_data = JSONExtractor.extract_json_from_text(response)
            if not json_data:
                return "Error: Failed to extract valid JSON from text"
            
            if not JSONExtractor.validate_expense_data(json_data):
                return "Error: Invalid expense data structure"
            
            logger.info(f"✅ Text processed: {len(json_data.get('items', []))} items found")
            return json.dumps(json_data)
            
        except Exception as e:
            logger.error(f"Text processing error: {e}")
            return f"Error extracting text expense: {str(e)}"