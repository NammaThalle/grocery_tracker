"""
Models package for the Grocery Bot system.

This package contains all data models, utilities, and processing classes.
It's organized by functionality to maintain clean separation of concerns.
"""

# Base models and common structures
from .base import BaseDataModel, AgentResult

# Expense-related models
from .expense import ExpenseItem, ExpenseData, ProcessedItem

# Processing utilities
from .processors import ItemProcessor

# Date handling utilities
from .date_utils import DateParser

# JSON utilities
from .json_utils import JSONExtractor

# Backward compatibility exports - maintain same interface
# This ensures existing code continues to work without changes
ExpenseItem = ExpenseItem
ExpenseData = ExpenseData
ProcessedItem = ProcessedItem
AgentResult = AgentResult
ItemProcessor = ItemProcessor
DateParser = DateParser
JSONExtractor = JSONExtractor

__all__ = [
    # Base classes
    'BaseDataModel',
    'AgentResult',
    
    # Expense models
    'ExpenseItem',
    'ExpenseData', 
    'ProcessedItem',
    
    # Utility classes
    'ItemProcessor',
    'DateParser',
    'JSONExtractor'
]