"""
Tool registry for managing available tools.
"""
import logging

from typing import Dict
from .base import BaseTool
from .process_receipt import ProcessReceiptTool
from .extract_text_expense import ExtractTextExpenseTool
from .save_to_sheets import SaveToSheetsTool

logger = logging.getLogger(__name__)

class ToolRegistry:
    """Registry for managing available tools"""
    
    def __init__(self):
        self.tools = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default tools"""
        default_tools = [
            ProcessReceiptTool(),
            ExtractTextExpenseTool(),
            SaveToSheetsTool()
        ]
        
        for tool in default_tools:
            self.register_tool(tool)
    
    def register_tool(self, tool: BaseTool):
        """Register a new tool"""
        self.tools[tool.name] = tool
        logger.info(f"🔧 Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> BaseTool:
        """Get a tool by name"""
        return self.tools.get(name) # type: ignore
    
    def list_tools(self) -> Dict[str, str]:
        """List all available tools"""
        return {name: tool.description for name, tool in self.tools.items()}
    
    async def execute_tool(self, name: str, **kwargs) -> str:
        """Execute a tool by name"""
        tool = self.get_tool(name)
        if not tool:
            return f"Error: Tool '{name}' not found"
        
        try:
            return await tool.execute(**kwargs)
        except Exception as e:
            logger.error(f"Tool execution error ({name}): {e}")
            return f"Error executing tool {name}: {str(e)}"