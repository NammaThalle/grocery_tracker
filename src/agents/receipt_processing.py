"""
Agent specialized in processing receipt images.
"""
import json
import logging

from datetime import datetime
from .base import BaseAgent
from src.models import AgentResult, JSONExtractor

logger = logging.getLogger(__name__)

class ReceiptProcessingAgent(BaseAgent):
    """Agent specialized in processing receipt images"""
    
    def __init__(self):
        super().__init__(
            name="Receipt Processing Agent",
            description="Processes grocery receipt images and extracts expense data",
            tools=["process_receipt", "save_to_sheets"]
        )
    
    async def execute(self, image_data: str, message_date: str = None, **kwargs) -> AgentResult: # type: ignore
        """Execute receipt processing workflow"""
        try:
            logger.info(f"🧠 {self.name} starting receipt processing...")
            
            # Step 1: Extract data from receipt
            logger.info("📸 Extracting data from receipt image...")
            extract_result = await self._execute_tool("process_receipt", image_data=image_data)
            
            if extract_result.startswith("Error"):
                return AgentResult(
                    success=False,
                    message="Failed to extract data from receipt",
                    error=extract_result
                )
            
            # Step 2: Parse and validate extracted data
            expense_data = JSONExtractor.extract_json_from_text(extract_result)
            if not expense_data:
                return AgentResult(
                    success=False,
                    message="Failed to parse extracted data",
                    error="Invalid JSON response from extraction"
                )
            
            # Step 3: Save to Google Sheets
            logger.info("💾 Saving data to Google Sheets...")
            save_result = await self._execute_tool(
                "save_to_sheets",
                expense_data=json.dumps(expense_data),
                message_date=message_date or datetime.now().strftime('%Y-%m-%d')
            )
            
            if save_result.startswith("Error"):
                return AgentResult(
                    success=False,
                    message="Data extracted but failed to save",
                    data=expense_data,
                    error=save_result
                )
            
            # Step 4: Generate success response
            items_count = len(expense_data.get('items', []))
            total = expense_data.get('total', 'N/A')
            store = expense_data.get('store', 'Unknown')
            receipt_date = expense_data.get('date', 'N/A')
            
            success_message = (
                f"✅ Receipt processed successfully!\n\n"
                f"📅 Date: {receipt_date if receipt_date != 'N/A' else message_date}\n"
                f"🏪 Store: {store}\n"
                f"📝 Items: {items_count}\n"
                f"💰 Total: ₹{total}\n"
                f"📊 {save_result}"
            )
            
            return AgentResult(
                success=True,
                message=success_message,
                data=expense_data
            )
            
        except Exception as e:
            logger.error(f"Receipt agent error: {e}")
            return AgentResult(
                success=False,
                message="Receipt processing failed",
                error=str(e)
            )