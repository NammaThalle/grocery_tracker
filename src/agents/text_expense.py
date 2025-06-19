"""
Agent specialized in processing text expense entries.
"""
import json
import logging

from datetime import datetime
from .base import BaseAgent
from src.models import AgentResult, JSONExtractor

logger = logging.getLogger(__name__)

class TextExpenseAgent(BaseAgent):
    """Agent specialized in processing natural language expense entries"""
    
    def __init__(self):
        super().__init__(
            name="Text Expense Agent",
            description="Processes natural language expense entries",
            tools=["extract_text_expense", "save_to_sheets"]
        )
    
    async def execute(self, text: str, message_date: str = None, **kwargs) -> AgentResult: # type: ignore
        """Execute text expense processing workflow"""
        try:
            logger.info(f"🧠 {self.name} starting text processing...")
            
            # Step 1: Extract data from text
            logger.info("📝 Extracting expense data from text...")
            extract_result = await self._execute_tool("extract_text_expense", text=text)
            
            if extract_result.startswith("Error"):
                return AgentResult(
                    success=False,
                    message="Failed to extract expense data from text",
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
            
            success_message = (
                f"✅ Text expense processed successfully!\n\n"
                f"📅 Date: {message_date or datetime.now().strftime('%Y-%m-%d')}\n"
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
            logger.error(f"Text agent error: {e}")
            return AgentResult(
                success=False,
                message="Text expense processing failed",
                error=str(e)
            )