"""
Base agent class for the Grocery Bot system.
"""
import logging

from abc import ABC, abstractmethod
from typing import List
from src.models import AgentResult
from src.tools import ToolRegistry

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, name: str, description: str, tools: List[str]):
        self.name = name
        self.description = description
        self.tools = tools
        self.tool_registry = ToolRegistry()
        logger.info(f"🤖 Initialized agent: {name}")
    
    @abstractmethod
    async def execute(self, **kwargs) -> AgentResult:
        """Execute the agent with given parameters"""
        pass
    
    async def _execute_tool(self, tool_name: str, **kwargs) -> str:
        """Execute a tool safely"""
        try:
            return await self.tool_registry.execute_tool(tool_name, **kwargs)
        except Exception as e:
            logger.error(f"Tool execution failed ({tool_name}): {e}")
            return f"Error: Tool execution failed - {str(e)}"