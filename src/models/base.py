"""
Base model classes and common data structures.
"""
from pydantic import BaseModel
from dataclasses import dataclass
from typing import Dict, Optional

class BaseDataModel(BaseModel):
    """Base class for all Pydantic models with common configuration"""
    
    class Config:
        # Allow extra fields for flexibility
        extra = "allow"
        # Use enum values instead of names
        use_enum_values = True
        # Validate assignments
        validate_assignment = True

@dataclass
class AgentResult:
    """Result from agent execution"""
    success: bool
    message: str
    data: Optional[Dict] = None
    error: Optional[str] = None
    
    def is_success(self) -> bool:
        """Check if the operation was successful"""
        return self.success and not self.error
    
    def get_error_message(self) -> str:
        """Get formatted error message"""
        if self.error:
            return f"Error: {self.error}"
        elif not self.success:
            return f"Failed: {self.message}"
        return "No error"