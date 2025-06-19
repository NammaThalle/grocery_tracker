"""
Expense-related data models.
"""
from typing import List, Optional
from .base import BaseDataModel

class ExpenseItem(BaseDataModel):
    """Model for individual expense items"""
    name: str
    quantity: str = "1"
    unit: str = "pcs"
    total_price: float = 0.0
    
    @classmethod
    def model_validate(cls, data): # type: ignore
        """Custom validation to handle different input types"""
        if isinstance(data, dict):
            # Convert quantity to string if it's a number
            if 'quantity' in data and isinstance(data['quantity'], (int, float)):
                data['quantity'] = str(data['quantity'])
            
            # Ensure total_price is a float
            if 'total_price' in data:
                data['total_price'] = float(data['total_price'])
        
        return super().model_validate(data)
    
    def get_unit_price(self) -> float:
        """Calculate price per unit"""
        try:
            qty = float(self.quantity) if self.quantity.replace('.', '').isdigit() else 1.0
            return self.total_price / qty if qty > 0 else self.total_price
        except (ValueError, ZeroDivisionError):
            return self.total_price

class ExpenseData(BaseDataModel):
    """Model for complete expense data"""
    store: str = "Unknown"
    date: Optional[str] = None
    items: List[ExpenseItem] = []
    subtotal: Optional[float] = None
    total: Optional[float] = None
    payment_method: Optional[str] = None
    
    def get_total_amount(self) -> float:
        """Get the total amount, calculating from items if not provided"""
        if self.total is not None:
            return self.total
        
        # Calculate from items
        return sum(item.total_price for item in self.items)
    
    def get_item_count(self) -> int:
        """Get the number of items"""
        return len(self.items)
    
    def has_valid_items(self) -> bool:
        """Check if there are valid items with prices"""
        return any(item.total_price > 0 for item in self.items)

class ProcessedItem(BaseDataModel):
    """Model for processed items ready for sheets"""
    date: str
    original_name: str
    clean_name: str
    pieces: int
    unit_size: str
    total_quantity: str
    price_per_unit: float
    total_value: float
    
    def to_sheet_row(self) -> List[str]:
        """Convert to a list for Google Sheets row"""
        return [
            self.date,
            self.original_name,
            self.clean_name,
            str(self.pieces),
            self.unit_size,
            self.total_quantity,
            str(self.price_per_unit),
            str(self.total_value)
        ]
    
    @classmethod
    def get_sheet_headers(cls) -> List[str]:
        """Get the headers for Google Sheets"""
        return [
            'Date', 'Original Item Name', 'Item Name', 'Pieces', 
            'Unit Size', 'Total Quantity', 'Price', 'Value'
        ]