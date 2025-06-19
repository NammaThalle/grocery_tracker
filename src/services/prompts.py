"""
Service for managing AI prompts.
"""
import logging

from .base import BaseService

logger = logging.getLogger(__name__)

class PromptService(BaseService):
    """Service for managing AI prompts"""
    
    def __init__(self):
        super().__init__("Prompt Service")
    
    @staticmethod
    def get_receipt_processing_prompt() -> str:
        """Get prompt for receipt processing"""
        return """
        Analyze this grocery receipt and extract each item with detailed information in JSON format:
        {
            "store": "Store name from receipt",
            "date": "Receipt date (DD-MM-YYYY or any format visible)",
            "items": [
                {
                    "name": "Complete item name as written on receipt",
                    "quantity": "1", 
                    "unit": "kg/pcs/g/liters",
                    "total_price": 45.50
                }
            ],
            "subtotal": 105.50,
            "total": 110.78
        }
        
        Instructions:
        - Extract EVERY item exactly as written on receipt
        - Look for the receipt date - usually at top or bottom of receipt
        - For "total_price", use the TOTAL AMOUNT PAID for that item line (not per-unit price)
        - Example: If "Grapes-500g" costs ₹60, then total_price should be 60.0 (for the entire 500g)
        - Example: If "Lime-5pcs" costs ₹30, then total_price should be 30.0 (for all 5 pieces)
        - If quantity not clear, assume 1 and use "pcs" as unit
        - If date not visible, use "N/A"
        - Use numbers only for prices (no currency symbols)
        - Ensure all numeric values are proper numbers, not strings
        - Return ONLY valid JSON
        """
    
    @staticmethod
    def get_text_expense_prompt(text: str) -> str:
        """Get prompt for text expense processing"""
        return f"""
        Extract expense information from this text and format as detailed JSON:
        
        Text: "{text}"
        
        Format as JSON:
        {{
            "store": "Store name if mentioned, otherwise 'Manual Entry'",
            "items": [
                {{
                    "name": "Complete item name",
                    "quantity": "1",
                    "unit": "kg/pcs/g/liters", 
                    "total_price": 60.0
                }}
            ],
            "total": 130.0
        }}
        
        Instructions:
        - Extract all items with their prices
        - Determine appropriate units (kg for vegetables/fruits, pcs for countable items, g/ml for small quantities)
        - For "total_price", use the TOTAL amount spent on that item (not per-unit price)
        - Example: "Apples 2kg ₹120" → total_price should be 120.0 (for the entire 2kg)
        - Example: "5 oranges ₹50" → total_price should be 50.0 (for all 5 oranges)
        - Convert prices to numbers only (remove ₹, Rs, etc.)
        - If quantity mentioned, extract it properly
        - Ensure all numeric values are proper numbers, not strings
        - Return ONLY valid JSON
        """
    
    @staticmethod
    def get_custom_prompt(template: str, **kwargs) -> str:
        """Get a custom prompt with variable substitution"""
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing template variable: {e}")
            return template
    
    @staticmethod
    def validate_prompt(prompt: str) -> bool:
        """Validate that a prompt is not empty and has reasonable length"""
        if not prompt or not prompt.strip():
            return False
        
        # Check for reasonable length (not too short, not too long)
        stripped_prompt = prompt.strip()
        return 10 <= len(stripped_prompt) <= 10000
    
    async def health_check(self) -> bool:
        """Check if prompt service is healthy"""
        try:
            # Test that all static prompts are valid
            receipt_prompt = self.get_receipt_processing_prompt()
            text_prompt = self.get_text_expense_prompt("test")
            
            return (self.validate_prompt(receipt_prompt) and 
                   self.validate_prompt(text_prompt))
        except Exception as e:
            logger.error(f"Prompt service health check failed: {e}")
            return False