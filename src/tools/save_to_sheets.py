"""
Tool for saving expense data to Google Sheets.
"""
import json
import logging

from datetime import datetime
from .base import BaseTool
from src.services import GoogleSheetsService
from src.models import ExpenseData, ExpenseItem, ItemProcessor, DateParser

logger = logging.getLogger(__name__)

class SaveToSheetsTool(BaseTool):
    """Tool for saving expense data to Google Sheets"""
    
    def __init__(self):
        super().__init__(
            name="save_to_sheets",
            description="Save processed expense data to Google Sheets"
        )
        self.sheets_service = GoogleSheetsService()
    
    async def execute(self, expense_data: str = None, message_date: str = None, **kwargs) -> str: # type: ignore
        """Save expense data to Google Sheets"""
        try:
            if not expense_data:
                return "Error: No expense data provided"
            
            # Parse expense data
            try:
                data_dict = json.loads(expense_data)
                
                # Fix data types before validation
                if 'items' in data_dict:
                    for item in data_dict['items']:
                        # Convert quantity to string if it's a number
                        if 'quantity' in item and isinstance(item['quantity'], (int, float)):
                            item['quantity'] = str(item['quantity'])
                        
                        # Ensure total_price is a float
                        if 'total_price' in item:
                            item['total_price'] = float(item['total_price'])
                
                expense_data_obj = ExpenseData(**data_dict)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                return f"Error: Invalid JSON format - {str(e)}"
            except Exception as e:
                logger.error(f"Data validation error: {e}")
                return f"Error: Invalid data structure - {str(e)}"
            
            if not expense_data_obj.items:
                return "Error: No items found in expense data"
            
            # Determine expense date
            message_datetime = None
            if message_date:
                try:
                    message_datetime = datetime.strptime(message_date, '%Y-%m-%d')
                except ValueError:
                    pass
            
            expense_date = DateParser.determine_expense_date(expense_data_obj, message_datetime)
            
            # Process items
            processed_items = []
            for item_data in expense_data_obj.items:
                try:
                    item = ExpenseItem(**item_data.dict() if hasattr(item_data, 'dict') else item_data) # type: ignore
                    processed_item = ItemProcessor.create_processed_item(item, expense_date)
                    processed_items.append(processed_item)
                except Exception as e:
                    logger.error(f"Error processing item {item_data}: {e}")
                    continue
            
            if not processed_items:
                return "Error: No valid items to save"
            
            # Save to sheets
            result = await self.sheets_service.save_items(processed_items)
            
            logger.info(f"✅ Saved {len(processed_items)} items to sheets")
            return result
            
        except Exception as e:
            logger.error(f"Save to sheets error: {e}")
            return f"Error saving to sheets: {str(e)}"