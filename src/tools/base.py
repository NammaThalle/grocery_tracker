"""
Base tool class for the Grocery Bot system.
"""
from abc import ABC, abstractmethod

class BaseTool(ABC):
    """Abstract base class for all tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """Execute the tool with given parameters"""
        pass