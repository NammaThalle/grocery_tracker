"""
Service for Google Sheets operations.
"""
import asyncio
import logging

from typing import List
from src.models import ProcessedItem
from config import config, singleton
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from .base import BaseService

logger = logging.getLogger(__name__)

@singleton
class GoogleSheetsService(BaseService):
    """Service for Google Sheets operations - Singleton to reuse client"""
    
    def __init__(self):
        super().__init__("Google Sheets Service")
        self.credentials = Credentials.from_service_account_file(
            config.sheets_credentials_path,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        self.service = build('sheets', 'v4', credentials=self.credentials)
        self.spreadsheet_id = config.sheets_id
    
    async def save_items(self, items: List[ProcessedItem]) -> str: # type: ignore
        """Save processed items to Google Sheets"""
        try:
            if not items:
                return "No items to save"
            
            # Convert items to rows
            rows = []
            for item in items:
                row = [
                    item.date,
                    item.original_name,
                    item.clean_name,
                    str(item.pieces),
                    item.unit_size,
                    item.total_quantity,
                    str(item.price_per_unit),
                    str(item.total_value)
                ]
                rows.append(row)
            
            # Prepare request body
            body = {'values': rows}
            
            # Execute request in thread to avoid blocking
            def update_sheet():
                return self.service.spreadsheets().values().append(
                    spreadsheetId=self.spreadsheet_id,
                    range=config.sheets_range,
                    valueInputOption='RAW',
                    body=body
                ).execute()
            
            result = await asyncio.to_thread(update_sheet)
            rows_added = result.get('updates', {}).get('updatedRows', 0)
            
            logger.info(f"✅ Added {rows_added} rows to Google Sheets")
            return f"Successfully saved {rows_added} items to Google Sheets"
            
        except Exception as e:
            logger.error(f"❌ Google Sheets error: {e}")
            return f"Error saving to sheets: {str(e)}"
    
    async def create_headers_if_needed(self) -> None:
        """Create headers in the sheet if they don't exist"""
        try:
            def get_headers():
                return self.service.spreadsheets().values().get(
                    spreadsheetId=self.spreadsheet_id,
                    range='Sheet1!A1:H1'
                ).execute()
            
            result = await asyncio.to_thread(get_headers)
            
            if not result.get('values'):
                headers = [
                    'Date', 'Original Item Name', 'Item Name', 'Pieces', 
                    'Unit Size', 'Total Quantity', 'Price', 'Value'
                ]
                body = {'values': [headers]}
                
                def update_headers():
                    return self.service.spreadsheets().values().update(
                        spreadsheetId=self.spreadsheet_id,
                        range='Sheet1!A1:H1',
                        valueInputOption='RAW',
                        body=body
                    ).execute()
                
                await asyncio.to_thread(update_headers)
                logger.info("✅ Created sheet headers")
            else:
                logger.info("✅ Sheet headers already exist")
                
        except Exception as e:
            logger.error(f"❌ Header creation error: {e}")
    
    async def health_check(self) -> bool:
        """Check if Google Sheets service is healthy"""
        try:
            def test_connection():
                return self.service.spreadsheets().get(
                    spreadsheetId=self.spreadsheet_id
                ).execute()
            
            await asyncio.to_thread(test_connection)
            return True
        except Exception as e:
            logger.error(f"Google Sheets health check failed: {e}")
            return False