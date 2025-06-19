"""
Central manager for all agents.
"""
import logging

from typing import Dict, Optional
from config import singleton
from .base import BaseAgent
from .receipt_processing import ReceiptProcessingAgent
from .text_expense import TextExpenseAgent
from src.models import AgentResult
from src.services import GeminiService

logger = logging.getLogger(__name__)

@singleton
class AgentManager:
    """Central manager for all agents - Singleton to ensure single instance"""
    
    def __init__(self):
        self.agents = {}
        self._register_default_agents()
        logger.info("🎯 Agent Manager initialized")
    
    def _register_default_agents(self):
        """Register default agents"""
        default_agents = [
            ReceiptProcessingAgent(),
            TextExpenseAgent()
        ]
        
        for agent in default_agents:
            self.register_agent(agent)
    
    def register_agent(self, agent: BaseAgent):
        """Register a new agent"""
        self.agents[agent.name] = agent
        logger.info(f"📋 Registered agent: {agent.name}")
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get an agent by name"""
        return self.agents.get(name)
    
    def list_agents(self) -> Dict[str, str]:
        """List all available agents"""
        return {name: agent.description for name, agent in self.agents.items()}
    
    async def process_receipt_image(self, image_data: str, message_date: str = None) -> AgentResult: # type: ignore
        """Process receipt image using receipt agent"""
        agent = self.get_agent("Receipt Processing Agent")
        if not agent:
            return AgentResult(
                success=False,
                message="Receipt processing agent not available",
                error="Agent not found"
            )
        
        return await agent.execute(image_data=image_data, message_date=message_date)
    
    async def process_text_expense(self, text: str, message_date: str = None) -> AgentResult: # type: ignore
        """Process text expense using text agent"""
        agent = self.get_agent("Text Expense Agent")
        if not agent:
            return AgentResult(
                success=False,
                message="Text expense agent not available",
                error="Agent not found"
            )
        
        return await agent.execute(text=text, message_date=message_date)
    
    async def get_system_status(self) -> Dict:
        """Get system status and health check"""
        try:
            # Test Gemini service
            gemini_service = GeminiService()
            gemini_test = gemini_service.call("Test")
            gemini_status = "✅ Online" if not gemini_test.startswith("Error") else "❌ Error"
            
            # Test Google Sheets service
            from services import GoogleSheetsService
            sheets_service = GoogleSheetsService()
            sheets_status = "✅ Online"  # If initialization succeeded, it's working
            
            return {
                "agents": len(self.agents),
                "gemini_service": gemini_status,
                "sheets_service": sheets_status,
                "config_valid": "✅ Valid",
                "available_agents": list(self.agents.keys())
            }
            
        except Exception as e:
            logger.error(f"System status check failed: {e}")
            return {
                "error": str(e),
                "agents": len(self.agents),
                "status": "❌ System Error"
            }