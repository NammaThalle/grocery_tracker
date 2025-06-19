"""
Data processing utilities for grocery items.
"""
import re
import logging

from typing import Tuple
from .expense import ExpenseItem, ProcessedItem

logger = logging.getLogger(__name__)

class ItemProcessor:
    """Utility class for processing grocery items"""
    
    @staticmethod
    def clean_item_name(original_name: str) -> str:
        """Clean up item name by removing codes and quantities"""
        name = original_name
        
        # Remove prefixes like "BB VE", "SUNL", etc.
        name = re.sub(r'^[A-Z]{2,4}\s+(VE\s+)?', '', name)
        
        # Remove suffixes like "-1kg", "-5pcs", "150GRAM-1pcs"
        name = re.sub(r'-\d+[a-zA-Z]+$', '', name)
        name = re.sub(r'\d+[A-Z]+-\d+[a-z]+$', '', name)
        
        # Clean up "FR" (fresh) indicators
        name = re.sub(r'\bFR\s+', '', name)
        
        # Capitalize properly
        name = name.title().strip()
        
        # Handle specific cases
        replacements = {
            'DRAKSHE': 'Grapes',
            'KALINGAN': 'Black Grapes',
            'LIME': 'Lime',
            'TGHT': 'Sunlight Soap'
        }
        
        for old, new in replacements.items():
            if old in name.upper():
                name = new
                break
        
        return name if name else original_name
    
    @staticmethod
    def extract_package_info(item: ExpenseItem) -> Tuple[int, str, str]:
        """Extract pieces, unit size, and total quantity from item"""
        original_name = item.name
        extracted_quantity = item.quantity
        
        # Initialize defaults
        pieces = 1
        unit_size = "1pcs"
        total_quantity = "1pcs"
        
        # The number of packages actually bought
        packages_bought = int(extracted_quantity) if extracted_quantity.isdigit() else 1
        
        # Extract weight-based packages (grams/kg)
        kg_match = re.search(r'-(\d+(?:\.\d+)?)kg', original_name)
        gram_match = re.search(r'-(\d+)g', original_name) 
        gram_complex_match = re.search(r'(\d+)GRAM-(\d+)pcs', original_name)
        
        # Extract piece-based packages
        pcs_match = re.search(r'-(\d+)pcs', original_name)
        
        if kg_match:
            kg_per_package = float(kg_match.group(1))
            pieces = packages_bought
            unit_size = f"{kg_per_package}kg"
            total_quantity = f"{kg_per_package * packages_bought}kg"
            
        elif gram_match:
            grams_per_package = int(gram_match.group(1))
            pieces = packages_bought
            unit_size = f"{grams_per_package}g"
            
            total_grams = grams_per_package * packages_bought
            if total_grams >= 1000:
                total_quantity = f"{total_grams/1000}kg"
            else:
                total_quantity = f"{total_grams}g"
                
        elif gram_complex_match:
            grams_per_package = int(gram_complex_match.group(1))
            pieces = packages_bought
            unit_size = f"{grams_per_package}g"
            
            total_grams = grams_per_package * packages_bought
            if total_grams >= 1000:
                total_quantity = f"{total_grams/1000}kg"
            else:
                total_quantity = f"{total_grams}g"
                
        elif pcs_match:
            pcs_per_package = int(pcs_match.group(1))
            pieces = packages_bought
            unit_size = f"{pcs_per_package}pcs"
            total_quantity = f"{pcs_per_package * packages_bought}pcs"
            
        else:
            pieces = packages_bought
            unit_size = "1pcs"
            total_quantity = f"{packages_bought}pcs"
        
        return pieces, unit_size, total_quantity
    
    @staticmethod
    def create_processed_item(item: ExpenseItem, expense_date: str) -> ProcessedItem:
        """Create a processed item ready for Google Sheets"""
        clean_name = ItemProcessor.clean_item_name(item.name)
        pieces, unit_size, total_quantity = ItemProcessor.extract_package_info(item)
        
        total_price = item.total_price
        per_package_price = total_price / pieces if pieces > 0 else total_price
        
        return ProcessedItem(
            date=expense_date,
            original_name=item.name,
            clean_name=clean_name,
            pieces=pieces,
            unit_size=unit_size,
            total_quantity=total_quantity,
            price_per_unit=round(per_package_price, 2),
            total_value=round(total_price, 2)
        )
    
    @staticmethod
    def validate_item(item: ExpenseItem) -> Tuple[bool, str]:
        """Validate an expense item"""
        if not item.name or not item.name.strip():
            return False, "Item name cannot be empty"
        
        if item.total_price < 0:
            return False, "Item price cannot be negative"
        
        try:
            qty = float(item.quantity) if item.quantity.replace('.', '').isdigit() else 1.0
            if qty <= 0:
                return False, "Item quantity must be positive"
        except ValueError:
            return False, "Invalid quantity format"
        
        return True, "Valid item"