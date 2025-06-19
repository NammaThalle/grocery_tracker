"""
Date parsing and handling utilities.
"""
import re
import logging

from datetime import datetime
from typing import Optional
from .expense import ExpenseData

logger = logging.getLogger(__name__)

class DateParser:
    """Utility class for parsing dates from various formats"""
    
    @staticmethod
    def parse_receipt_date(date_string: str) -> Optional[datetime]:
        """Parse date from receipt in various formats"""
        if not date_string or date_string == 'N/A':
            return None
            
        # Clean the date string
        date_string = str(date_string).strip()
        
        # Common date formats found on receipts
        date_formats = [
            "%Y-%m-%d",      # 2024-06-18
            "%d-%m-%Y",      # 18-06-2024
            "%d/%m/%Y",      # 18/06/2024
            "%m/%d/%Y",      # 06/18/2024
            "%d.%m.%Y",      # 18.06.2024
            "%d-%m-%y",      # 18-06-24
            "%d/%m/%y",      # 18/06/24
            "%Y%m%d",        # 20240618
            "%d%m%Y",        # 18062024
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue
        
        # Try to extract date using regex patterns
        # Pattern: DD-MM-YYYY or DD/MM/YYYY
        date_pattern = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', date_string)
        if date_pattern:
            day, month, year = date_pattern.groups()
            try:
                return datetime(int(year), int(month), int(day))
            except ValueError:
                pass
        
        # Pattern: DD-MM-YY or DD/MM/YY
        date_pattern = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2})', date_string)
        if date_pattern:
            day, month, year = date_pattern.groups()
            try:
                # Assume 20xx for 2-digit years
                full_year = 2000 + int(year)
                return datetime(full_year, int(month), int(day))
            except ValueError:
                pass
        
        return None
    
    @staticmethod
    def determine_expense_date(expense_data: ExpenseData, message_date: Optional[datetime] = None) -> str:
        """Determine the appropriate date for the expense"""
        
        # First, try to get date from receipt data
        if expense_data.date and expense_data.date != 'N/A':
            parsed_date = DateParser.parse_receipt_date(expense_data.date)
            if parsed_date:
                return parsed_date.strftime("%Y-%m-%d")
        
        # If no valid receipt date, use message date
        if message_date:
            return message_date.strftime("%Y-%m-%d")
        
        # Fallback to current date
        return datetime.now().strftime("%Y-%m-%d")
    
    @staticmethod
    def validate_date_string(date_string: str) -> bool:
        """Validate if a date string can be parsed"""
        try:
            parsed = DateParser.parse_receipt_date(date_string)
            return parsed is not None
        except Exception:
            return False
    
    @staticmethod
    def format_date_for_display(date_string: str) -> str:
        """Format date for user-friendly display"""
        try:
            parsed = DateParser.parse_receipt_date(date_string)
            if parsed:
                return parsed.strftime("%B %d, %Y")  # e.g., "June 18, 2024"
            return date_string
        except Exception:
            return date_string
    
    @staticmethod
    def get_date_range_string(start_date: datetime, end_date: datetime) -> str:
        """Get a formatted date range string"""
        if start_date.date() == end_date.date():
            return start_date.strftime("%Y-%m-%d")
        return f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"