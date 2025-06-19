"""
Enhanced Tool Registry with dynamic tool selection and learning capabilities.
"""
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field

from .base import BaseTool
from .process_receipt import ProcessReceiptTool
from .extract_text_expense import ExtractTextExpenseTool
from .save_to_sheets import SaveToSheetsTool
from src.services import GeminiService

logger = logging.getLogger(__name__)

@dataclass
class ToolPerformance:
    """Track performance metrics for tools"""
    tool_name: str
    total_executions: int = 0
    successful_executions: int = 0
    average_execution_time: float = 0.0
    error_patterns: List[str] = field(default_factory=list)
    context_preferences: Dict[str, int] = field(default_factory=dict)
    
    @property
    def success_rate(self) -> float:
        return self.successful_executions / self.total_executions if self.total_executions > 0 else 0.0

@dataclass
class ToolRecommendation:
    """Tool recommendation with reasoning"""
    tool_name: str
    confidence: float
    reasoning: str
    expected_success_rate: float
    alternative_tools: List[str] = field(default_factory=list)

class AgenticToolRegistry:
    """Enhanced tool registry with intelligent tool selection and learning"""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.tool_performance: Dict[str, ToolPerformance] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.gemini_service = GeminiService()
        
        self._register_default_tools()
        logger.info("🔧 Agentic Tool Registry initialized")
    
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
        """Register a new tool with performance tracking"""
        self.tools[tool.name] = tool
        self.tool_performance[tool.name] = ToolPerformance(tool_name=tool.name)
        logger.info(f"🔧 Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def list_tools(self) -> Dict[str, str]:
        """List all available tools with descriptions and performance"""
        tool_list = {}
        for name, tool in self.tools.items():
            perf = self.tool_performance[name]
            tool_list[name] = f"{tool.description} | Success Rate: {perf.success_rate:.2f} | Executions: {perf.total_executions}"
        return tool_list
    
    async def recommend_tool(self, task_description: str, context: Dict[str, Any]) -> ToolRecommendation:
        """Intelligently recommend the best tool for a given task"""
        try:
            # Analyze task and context to recommend optimal tool
            recommendation_prompt = f"""
            Recommend the best tool for this task based on context and historical performance:
            
            Task: {task_description}
            Context: {json.dumps(context, indent=2)}
            
            Available Tools:
            {json.dumps(self.list_tools(), indent=2)}
            
            Tool Performance History:
            {json.dumps({name: {"success_rate": perf.success_rate, "total_executions": perf.total_executions} for name, perf in self.tool_performance.items()}, indent=2)}
            
            Consider:
            1. Task requirements vs tool capabilities
            2. Historical success rates for similar contexts
            3. Tool specializations and strengths
            4. Context-specific performance patterns
            5. Complexity and reliability requirements
            
            Recommend the best tool with reasoning:
            {{
                "recommended_tool": "tool_name",
                "confidence": 0.0-1.0,
                "reasoning": "detailed explanation",
                "expected_success_rate": 0.0-1.0,
                "alternative_tools": ["backup1", "backup2"]
            }}
            """
            
            response = self.gemini_service.call(recommendation_prompt)
            recommendation_data = json.loads(response[response.find('{'):response.rfind('}')+1])
            
            return ToolRecommendation(
                tool_name=recommendation_data.get("recommended_tool", ""),
                confidence=recommendation_data.get("confidence", 0.5),
                reasoning=recommendation_data.get("reasoning", "AI recommendation"),
                expected_success_rate=recommendation_data.get("expected_success_rate", 0.5),
                alternative_tools=recommendation_data.get("alternative_tools", [])
            )
            
        except Exception as e:
            logger.warning(f"⚠️ Tool recommendation failed, using fallback: {e}")
            # Fallback recommendation based on simple heuristics
            return self._fallback_tool_recommendation(task_description, context)
    
    def _fallback_tool_recommendation(self, task_description: str, context: Dict[str, Any]) -> ToolRecommendation:
        """Fallback tool recommendation using simple heuristics"""
        task_lower = task_description.lower()
        
        if "receipt" in task_lower or "image" in task_lower:
            return ToolRecommendation(
                tool_name="process_receipt",
                confidence=0.7,
                reasoning="Fallback: Task mentions receipt or image processing",
                expected_success_rate=0.7,
                alternative_tools=["extract_text_expense"]
            )
        elif "text" in task_lower or "extract" in task_lower:
            return ToolRecommendation(
                tool_name="extract_text_expense",
                confidence=0.7,
                reasoning="Fallback: Task mentions text processing",
                expected_success_rate=0.7,
                alternative_tools=["process_receipt"]
            )
        elif "save" in task_lower or "sheets" in task_lower:
            return ToolRecommendation(
                tool_name="save_to_sheets",
                confidence=0.8,
                reasoning="Fallback: Task mentions saving to sheets",
                expected_success_rate=0.8,
                alternative_tools=[]
            )
        else:
            # Return highest performing tool as default
            best_tool = max(self.tool_performance.items(), key=lambda x: x[1].success_rate)
            return ToolRecommendation(
                tool_name=best_tool[0],
                confidence=0.5,
                reasoning=f"Fallback: Using highest performing tool ({best_tool[1].success_rate:.2f} success rate)",
                expected_success_rate=best_tool[1].success_rate,
                alternative_tools=[]
            )
    
    async def execute_tool_with_learning(self, name: str, **kwargs) -> Tuple[str, Dict[str, Any]]:
        """Execute tool with performance tracking and learning"""
        start_time = datetime.now()
        execution_context = {
            "tool_name": name,
            "start_time": start_time.isoformat(),
            "parameters": list(kwargs.keys()),
            "context_type": self._classify_execution_context(**kwargs)
        }
        
        try:
            # Execute the tool
            result = await self.execute_tool(name, **kwargs)
            
            # Record successful execution
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            self._record_successful_execution(name, execution_time, execution_context)
            
            execution_metadata = {
                "success": True,
                "execution_time": execution_time,
                "context_type": execution_context["context_type"]
            }
            
            return result, execution_metadata
            
        except Exception as e:
            # Record failed execution
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            self._record_failed_execution(name, str(e), execution_context)
            
            execution_metadata = {
                "success": False,
                "execution_time": execution_time,
                "error": str(e),
                "context_type": execution_context["context_type"]
            }
            
            return f"Error executing tool {name}: {str(e)}", execution_metadata
    
    async def execute_tool(self, name: str, **kwargs) -> str:
        """Execute a tool by name (legacy method)"""
        tool = self.get_tool(name)
        if not tool:
            return f"Error: Tool '{name}' not found"
        
        try:
            return await tool.execute(**kwargs)
        except Exception as e:
            logger.error(f"Tool execution error ({name}): {e}")
            return f"Error executing tool {name}: {str(e)}"
    
    def _classify_execution_context(self, **kwargs) -> str:
        """Classify the execution context for learning purposes"""
        if "image_data" in kwargs:
            return "image_processing"
        elif "text" in kwargs and len(str(kwargs["text"])) > 100:
            return "long_text_processing"
        elif "text" in kwargs:
            return "short_text_processing"
        elif "expense_data" in kwargs:
            return "data_saving"
        else:
            return "unknown"
    
    def _record_successful_execution(self, tool_name: str, execution_time: float, context: Dict[str, Any]):
        """Record a successful tool execution"""
        if tool_name in self.tool_performance:
            perf = self.tool_performance[tool_name]
            perf.total_executions += 1
            perf.successful_executions += 1
            
            # Update average execution time
            perf.average_execution_time = (
                (perf.average_execution_time * (perf.successful_executions - 1) + execution_time) 
                / perf.successful_executions
            )
            
            # Track context preferences
            context_type = context["context_type"]
            perf.context_preferences[context_type] = perf.context_preferences.get(context_type, 0) + 1
        
        # Add to execution history
        self.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "success": True,
            "execution_time": execution_time,
            "context": context
        })
        
        # Maintain history size
        if len(self.execution_history) > 1000:
            self.execution_history = self.execution_history[-500:]
    
    def _record_failed_execution(self, tool_name: str, error: str, context: Dict[str, Any]):
        """Record a failed tool execution"""
        if tool_name in self.tool_performance:
            perf = self.tool_performance[tool_name]
            perf.total_executions += 1
            
            # Track error patterns
            if len(perf.error_patterns) < 10:  # Keep last 10 error patterns
                perf.error_patterns.append(error[:100])  # Truncate long errors
        
        # Add to execution history
        self.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "success": False,
            "error": error,
            "context": context
        })
    
    def get_tool_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics about tool usage and performance"""
        analytics = {
            "total_tools": len(self.tools),
            "total_executions": sum(perf.total_executions for perf in self.tool_performance.values()),
            "overall_success_rate": 0.0,
            "tool_performance": {},
            "context_analysis": {},
            "execution_trends": {}
        }
        
        # Calculate overall success rate
        total_executions = sum(perf.total_executions for perf in self.tool_performance.values())
        total_successes = sum(perf.successful_executions for perf in self.tool_performance.values())
        analytics["overall_success_rate"] = total_successes / total_executions if total_executions > 0 else 0.0
        
        # Tool performance details
        for name, perf in self.tool_performance.items():
            analytics["tool_performance"][name] = {
                "success_rate": perf.success_rate,
                "total_executions": perf.total_executions,
                "average_execution_time": perf.average_execution_time,
                "recent_errors": perf.error_patterns[-3:],  # Last 3 errors
                "preferred_contexts": perf.context_preferences
            }
        
        # Context analysis
        context_stats = {}
        for execution in self.execution_history[-100:]:  # Last 100 executions
            context_type = execution.get("context", {}).get("context_type", "unknown")
            if context_type not in context_stats:
                context_stats[context_type] = {"total": 0, "successes": 0}
            
            context_stats[context_type]["total"] += 1
            if execution["success"]:
                context_stats[context_type]["successes"] += 1
        
        analytics["context_analysis"] = {
            context: {
                "success_rate": stats["successes"] / stats["total"] if stats["total"] > 0 else 0,
                "total_executions": stats["total"]
            }
            for context, stats in context_stats.items()
        }
        
        # Execution trends (last 24 hours)
        recent_executions = [
            e for e in self.execution_history 
            if datetime.fromisoformat(e["timestamp"]) > datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        ]
        
        analytics["execution_trends"] = {
            "executions_today": len(recent_executions),
            "successes_today": len([e for e in recent_executions if e["success"]]),
            "most_used_tool_today": max(
                set(e["tool_name"] for e in recent_executions),
                key=lambda tool: len([e for e in recent_executions if e["tool_name"] == tool])
            ) if recent_executions else None
        }
        
        return analytics
    
    async def optimize_tool_selection(self) -> Dict[str, Any]:
        """Analyze tool usage patterns and provide optimization recommendations"""
        analytics = self.get_tool_analytics()
        
        optimization_prompt = f"""
        Analyze these tool usage patterns and provide optimization recommendations:
        
        Tool Analytics: {json.dumps(analytics, indent=2)}
        
        Identify:
        1. Underperforming tools and possible causes
        2. Context-specific performance patterns
        3. Opportunities for improvement
        4. Potential tool gaps or redundancies
        5. Recommendations for better tool selection
        
        Provide actionable insights for optimizing the tool ecosystem.
        """
        
        try:
            optimization_response = self.gemini_service.call(optimization_prompt)
            
            return {
                "analytics_summary": analytics,
                "optimization_insights": optimization_response,
                "recommendations": {
                    "low_performing_tools": [
                        name for name, perf in self.tool_performance.items() 
                        if perf.success_rate < 0.7 and perf.total_executions > 5
                    ],
                    "high_performing_tools": [
                        name for name, perf in self.tool_performance.items() 
                        if perf.success_rate > 0.9 and perf.total_executions > 5
                    ],
                    "optimization_priority": "high" if analytics["overall_success_rate"] < 0.8 else "medium"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Tool optimization analysis failed: {e}")
            return {
                "analytics_summary": analytics,
                "error": "Optimization analysis failed",
                "recommendations": {
                    "optimization_priority": "unknown"
                }
            }

# For backward compatibility
ToolRegistry = AgenticToolRegistry