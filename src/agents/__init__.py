"""
Agentic Agents package for the AI Grocery Bot system.

This package contains intelligent agents with planning, reasoning, and learning capabilities.
Each agent can dynamically create execution plans, adapt to failures, and learn from experience.
"""
from .base import AgenticBaseAgent, Task, TaskType, Plan, AgentMemory
from .receipt_processing import AgenticReceiptProcessingAgent
from .text_expense import AgenticTextExpenseAgent
from .manager import AgenticAgentManager

# Backward compatibility exports
ReceiptProcessingAgent = AgenticReceiptProcessingAgent
TextExpenseAgent = AgenticTextExpenseAgent
AgentManager = AgenticAgentManager

__all__ = [
    # Agentic base classes
    'AgenticBaseAgent',
    'Task',
    'TaskType', 
    'Plan',
    'AgentMemory',
    
    # Agentic agent implementations
    'AgenticReceiptProcessingAgent',
    'AgenticTextExpenseAgent',
    'AgenticAgentManager',
    
    # Backward compatibility
    'ReceiptProcessingAgent',
    'TextExpenseAgent',
    'AgentManager'
]