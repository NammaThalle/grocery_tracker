"""
Agentic Tools package for the AI Grocery Bot system.

This package contains intelligent tools with performance tracking and dynamic selection.
Tools can learn from usage patterns and provide recommendations for optimal selection.
"""
from .base import BaseTool
from .process_receipt import ProcessReceiptTool
from .extract_text_expense import ExtractTextExpenseTool
from .save_to_sheets import SaveToSheetsTool
from .registry import AgenticToolRegistry, ToolPerformance, ToolRecommendation

# Backward compatibility exports
ToolRegistry = AgenticToolRegistry

__all__ = [
    # Base tool classes
    'BaseTool',
    
    # Tool implementations
    'ProcessReceiptTool',
    'ExtractTextExpenseTool',
    'SaveToSheetsTool',
    
    # Agentic tool management
    'AgenticToolRegistry',
    'ToolPerformance',
    'ToolRecommendation',
    
    # Backward compatibility
    'ToolRegistry'
]