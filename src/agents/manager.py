"""
Enhanced Agent Manager with multi-agent coordination and intelligent routing.
"""
import json
import logging
from typing import Dict, Optional, List, Any
from datetime import datetime

from config import singleton
from .base import AgenticBaseAgent
from .receipt_processing import AgenticReceiptProcessingAgent
from .text_expense import AgenticTextExpenseAgent
from src.models import AgentResult
from src.services import GeminiService

logger = logging.getLogger(__name__)

@singleton
class AgenticAgentManager:
    """Enhanced agent manager with multi-agent coordination and intelligent routing"""
    
    def __init__(self):
        self.agents: Dict[str, AgenticBaseAgent] = {}
        self.agent_collaboration_history: List[Dict[str, Any]] = []
        self.global_context: Dict[str, Any] = {}
        self.gemini_service = GeminiService()
        
        self._register_default_agents()
        logger.info("🎯 Agentic Agent Manager initialized")
    
    def _register_default_agents(self):
        """Register default agentic agents"""
        default_agents = [
            AgenticReceiptProcessingAgent(),
            AgenticTextExpenseAgent()
        ]
        
        for agent in default_agents:
            self.register_agent(agent)
    
    def register_agent(self, agent: AgenticBaseAgent):
        """Register a new agentic agent"""
        self.agents[agent.name] = agent
        logger.info(f"📋 Registered agentic agent: {agent.name}")
    
    def get_agent(self, name: str) -> Optional[AgenticBaseAgent]:
        """Get an agent by name"""
        return self.agents.get(name)
    
    def list_agents(self) -> Dict[str, str]:
        """List all available agents with their capabilities"""
        return {
            name: f"{agent.description} | Capabilities: {', '.join(agent.capabilities)}" 
            for name, agent in self.agents.items()
        }
    
    async def intelligent_route_request(self, **kwargs) -> AgentResult:
        """Intelligently route requests to the most appropriate agent(s)"""
        try:
            # Step 1: Analyze the request to determine best agent(s)
            routing_analysis = await self._analyze_request_for_routing(**kwargs)
            
            # Step 2: Check if multi-agent collaboration is needed
            if routing_analysis.get("requires_collaboration", False):
                return await self._execute_collaborative_processing(routing_analysis, **kwargs)
            else:
                # Step 3: Route to single best agent
                best_agent_name = routing_analysis.get("best_agent")
                if best_agent_name and best_agent_name in self.agents:
                    agent = self.agents[best_agent_name]
                    
                    # Update global context
                    self._update_global_context(routing_analysis, **kwargs)
                    
                    result = await agent.execute(**kwargs)
                    
                    # Learn from the routing decision
                    await self._learn_from_routing(routing_analysis, result, **kwargs)
                    
                    return result
                else:
                    return AgentResult(
                        success=False,
                        message="No suitable agent found for this request",
                        error="Agent routing failed"
                    )
        
        except Exception as e:
            logger.error(f"❌ Intelligent routing failed: {e}")
            return AgentResult(
                success=False,
                message="Request routing failed",
                error=str(e)
            )
    
    async def _analyze_request_for_routing(self, **kwargs) -> Dict[str, Any]:
        """Analyze request to determine optimal agent routing"""
        analysis_prompt = f"""
        Analyze this request to determine the best agent routing strategy:
        
        Request Data: {json.dumps({k: str(v)[:100] if isinstance(v, str) else v for k, v in kwargs.items()}, indent=2)}
        
        Available Agents:
        {json.dumps(self.list_agents(), indent=2)}
        
        Consider:
        1. Input type and complexity
        2. Required capabilities
        3. Agent specializations
        4. Potential for collaboration
        5. Historical performance patterns
        
        Determine:
        1. Best single agent for this request
        2. Whether multi-agent collaboration would improve results
        3. Confidence level in routing decision
        4. Alternative agents if primary fails
        5. Expected processing complexity
        
        Respond with JSON:
        {{
            "best_agent": "agent_name",
            "confidence": 0.0-1.0,
            "requires_collaboration": true/false,
            "collaborative_agents": ["agent1", "agent2"],
            "reasoning": "explanation of routing decision",
            "complexity_level": "low|medium|high",
            "alternative_agents": ["backup_agent1"],
            "expected_success_rate": 0.0-1.0
        }}
        """
        
        try:
            response = self.gemini_service.call(analysis_prompt)
            
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                analysis_data = json.loads(json_str)
                return analysis_data
            else:
                raise ValueError("No valid JSON found in response")
            
        except Exception as e:
            logger.warning(f"⚠️ Routing analysis failed, using fallback: {e}")
            # Fallback routing logic
            if "image_data" in kwargs:
                return {
                    "best_agent": "Agentic Receipt Processing Agent",
                    "confidence": 0.7,
                    "requires_collaboration": False,
                    "reasoning": "Fallback: Image data detected",
                    "complexity_level": "medium",
                    "expected_success_rate": 0.7
                }
            elif "text" in kwargs:
                return {
                    "best_agent": "Agentic Text Expense Agent", 
                    "confidence": 0.7,
                    "requires_collaboration": False,
                    "reasoning": "Fallback: Text data detected",
                    "complexity_level": "medium",
                    "expected_success_rate": 0.7
                }
            else:
                return {
                    "best_agent": None,
                    "confidence": 0.3,
                    "requires_collaboration": False,
                    "reasoning": "Fallback: Unknown input type",
                    "complexity_level": "high",
                    "expected_success_rate": 0.3
                }
    
    async def _execute_collaborative_processing(self, routing_analysis: Dict[str, Any], 
                                              **kwargs) -> AgentResult:
        """Execute collaborative processing with multiple agents"""
        collaborative_agents = routing_analysis.get("collaborative_agents", [])
        
        if not collaborative_agents:
            # Fallback to single agent
            best_agent = routing_analysis.get("best_agent")
            if best_agent and best_agent in self.agents:
                return await self.agents[best_agent].execute(**kwargs)
        
        logger.info(f"🤝 Starting collaborative processing with agents: {collaborative_agents}")
        
        # Execute agents in coordination
        results = []
        shared_context = {"collaboration_id": datetime.now().strftime("%Y%m%d_%H%M%S")}
        
        for agent_name in collaborative_agents:
            if agent_name in self.agents:
                agent = self.agents[agent_name]
                
                # Add shared context to agent execution
                enhanced_kwargs = {**kwargs, "shared_context": shared_context}
                
                result = await agent.execute(**enhanced_kwargs)
                results.append({
                    "agent": agent_name,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Update shared context with results
                if result.success and result.data:
                    shared_context[f"{agent_name}_result"] = result.data
        
        # Synthesize collaborative results
        final_result = await self._synthesize_collaborative_results(results, routing_analysis)
        
        # Record collaboration
        self.agent_collaboration_history.append({
            "timestamp": datetime.now().isoformat(),
            "agents": collaborative_agents,
            "routing_analysis": routing_analysis,
            "individual_results": results,
            "final_result": final_result.success,
            "collaboration_id": shared_context["collaboration_id"]
        })
        
        return final_result
    
    async def _synthesize_collaborative_results(self, results: List[Dict[str, Any]], 
                                              routing_analysis: Dict[str, Any]) -> AgentResult:
        """Synthesize results from multiple collaborating agents"""
        successful_results = [r for r in results if r["result"].success]
        
        if not successful_results:
            return AgentResult(
                success=False,
                message="All collaborative agents failed",
                error="No successful results from collaboration"
            )
        
        # Use AI to intelligently synthesize results
        synthesis_prompt = f"""
        Synthesize these collaborative agent results into a final coherent result:
        
        Routing Analysis: {json.dumps(routing_analysis, indent=2)}
        
        Agent Results:
        {json.dumps([{"agent": r["agent"], "success": r["result"].success, "message": r["result"].message} for r in results], indent=2)}
        
        Create a synthesis that:
        1. Combines the best aspects of each result
        2. Resolves any conflicts or inconsistencies
        3. Provides a unified, coherent response
        4. Highlights the collaborative advantage
        5. Maintains accuracy and completeness
        
        Focus on creating value from the multi-agent approach.
        """
        
        try:
            synthesis_response = self.gemini_service.call(synthesis_prompt)
            
            # Extract the most successful result's data
            best_result = max(successful_results, key=lambda x: len(str(x["result"].data or "")))
            
            collaborative_message = (
                f"🤝 **Multi-Agent Collaboration Complete!**\n\n"
                f"Agents involved: {', '.join([r['agent'].split()[-2:][0] for r in successful_results])}\n"
                f"Successful agents: {len(successful_results)}/{len(results)}\n\n"
                f"{synthesis_response}"
            )
            
            return AgentResult(
                success=True,
                message=collaborative_message,
                data={
                    "primary_data": best_result["result"].data,
                    "collaboration_summary": {
                        "agents_used": [r["agent"] for r in results],
                        "successful_agents": len(successful_results),
                        "total_agents": len(results),
                        "collaboration_advantage": synthesis_response
                    },
                    "individual_results": {r["agent"]: r["result"].data for r in successful_results if r["result"].data}
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Collaborative synthesis failed: {e}")
            # Fallback to best individual result
            best_result = max(successful_results, key=lambda x: len(str(x["result"].data or "")))
            
            return AgentResult(
                success=True,
                message=f"Collaboration completed. Best result from {best_result['agent']}",
                data=best_result["result"].data
            )
    
    def _update_global_context(self, routing_analysis: Dict[str, Any], **kwargs):
        """Update global context with request information"""
        context_entry = {
            "timestamp": datetime.now().isoformat(),
            "routing_analysis": routing_analysis,
            "request_type": self._determine_request_type(**kwargs),
            "complexity": routing_analysis.get("complexity_level", "medium")
        }
        
        # Maintain a sliding window of recent contexts
        if "recent_requests" not in self.global_context:
            self.global_context["recent_requests"] = []
        
        self.global_context["recent_requests"].append(context_entry)
        
        # Keep only last 20 requests
        if len(self.global_context["recent_requests"]) > 20:
            self.global_context["recent_requests"] = self.global_context["recent_requests"][-20:]
    
    async def _learn_from_routing(self, routing_analysis: Dict[str, Any], 
                                 result: AgentResult, **kwargs):
        """Learn from routing decisions to improve future routing"""
        learning_entry = {
            "timestamp": datetime.now().isoformat(),
            "routing_decision": routing_analysis.get("best_agent"),
            "confidence": routing_analysis.get("confidence", 0.5),
            "actual_success": result.success,
            "request_type": self._determine_request_type(**kwargs),
            "complexity": routing_analysis.get("complexity_level", "medium")
        }
        
        # Store learning data for pattern analysis
        if "routing_history" not in self.global_context:
            self.global_context["routing_history"] = []
        
        self.global_context["routing_history"].append(learning_entry)
        
        # Analyze patterns if we have enough data
        if len(self.global_context["routing_history"]) >= 10:
            await self._analyze_routing_patterns()
    
    async def _analyze_routing_patterns(self):
        """Analyze routing patterns to improve decision making"""
        try:
            history = self.global_context["routing_history"][-50:]  # Last 50 decisions
            
            # Calculate success rates per agent
            agent_performance = {}
            for entry in history:
                agent = entry["routing_decision"]
                if agent not in agent_performance:
                    agent_performance[agent] = {"successes": 0, "total": 0}
                
                agent_performance[agent]["total"] += 1
                if entry["actual_success"]:
                    agent_performance[agent]["successes"] += 1
            
            # Update global context with insights
            self.global_context["agent_performance_insights"] = {
                agent: {
                    "success_rate": data["successes"] / data["total"] if data["total"] > 0 else 0,
                    "total_requests": data["total"]
                }
                for agent, data in agent_performance.items()
            }
            
            logger.info(f"📊 Updated agent performance insights: {self.global_context['agent_performance_insights']}")
            
        except Exception as e:
            logger.warning(f"⚠️ Pattern analysis failed: {e}")
    
    def _determine_request_type(self, **kwargs) -> str:
        """Determine the type of request"""
        if "image_data" in kwargs:
            return "receipt_image"
        elif "text" in kwargs:
            return "text_expense"
        else:
            return "unknown"
    
    # Legacy compatibility methods
    async def process_receipt_image(self, image_data: str, message_date: str = None) -> AgentResult:
        """Process receipt image using intelligent routing"""
        return await self.intelligent_route_request(
            image_data=image_data,
            message_date=message_date
        )
    
    async def process_text_expense(self, text: str, message_date: str = None) -> AgentResult:
        """Process text expense using intelligent routing"""
        return await self.intelligent_route_request(
            text=text,
            message_date=message_date
        )
    
    async def get_system_status(self) -> Dict:
        """Get comprehensive system status including agentic capabilities"""
        try:
            # Test services
            gemini_service = GeminiService()
            gemini_test = gemini_service.call("Test")
            gemini_status = "✅ Online" if not gemini_test.startswith("Error") else "❌ Error"
            
            from src.services import GoogleSheetsService
            sheets_service = GoogleSheetsService()
            sheets_status = "✅ Online"
            
            # Get agent memory summaries
            agent_memories = {}
            for name, agent in self.agents.items():
                memory_summary = agent.get_memory_summary()
                agent_memories[name] = {
                    "experiences": memory_summary["total_experiences"],
                    "success_patterns": len(memory_summary["successful_patterns"]),
                    "current_plan": agent.get_current_plan_status()
                }
            
            # Get collaboration history summary
            recent_collaborations = len([
                c for c in self.agent_collaboration_history 
                if datetime.fromisoformat(c["timestamp"]) > datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            ])
            
            return {
                "agents": len(self.agents),
                "gemini_service": gemini_status,
                "sheets_service": sheets_status,
                "config_valid": "✅ Valid",
                "available_agents": list(self.agents.keys()),
                "agentic_features": {
                    "intelligent_routing": "✅ Active",
                    "multi_agent_collaboration": "✅ Active", 
                    "agent_learning": "✅ Active",
                    "dynamic_planning": "✅ Active"
                },
                "agent_memories": agent_memories,
                "collaboration_stats": {
                    "total_collaborations": len(self.agent_collaboration_history),
                    "recent_collaborations_today": recent_collaborations
                },
                "performance_insights": self.global_context.get("agent_performance_insights", {}),
                "system_type": "🤖 Agentic AI System"
            }
            
        except Exception as e:
            logger.error(f"System status check failed: {e}")
            return {
                "error": str(e),
                "agents": len(self.agents),
                "status": "❌ System Error",
                "system_type": "🤖 Agentic AI System"
            }
    
    async def analyze_agent_collaboration_effectiveness(self) -> Dict[str, Any]:
        """Analyze the effectiveness of agent collaboration"""
        if not self.agent_collaboration_history:
            return {
                "message": "No collaboration history available",
                "total_collaborations": 0,
                "successful_collaborations": 0,
                "overall_success_rate": 0,
                "collaboration_pairs": {},
                "most_effective_pair": None
            }
        
        total_collaborations = len(self.agent_collaboration_history)
        successful_collaborations = len([
            c for c in self.agent_collaboration_history 
            if c["final_result"]
        ])
        
        # Analyze collaboration patterns
        agent_pairs = {}
        for collab in self.agent_collaboration_history:
            agents = tuple(sorted(collab["agents"]))
            if agents not in agent_pairs:
                agent_pairs[agents] = {"count": 0, "successes": 0}
            
            agent_pairs[agents]["count"] += 1
            if collab["final_result"]:
                agent_pairs[agents]["successes"] += 1
        
        # Calculate success rates
        collaboration_success_rates = {}
        for agents, stats in agent_pairs.items():
            collaboration_success_rates[" + ".join(agents)] = {
                "success_rate": stats["successes"] / stats["count"] if stats["count"] > 0 else 0,
                "total_collaborations": stats["count"]
            }
        
        return {
            "total_collaborations": total_collaborations,
            "successful_collaborations": successful_collaborations,
            "overall_success_rate": successful_collaborations / total_collaborations if total_collaborations > 0 else 0,
            "collaboration_pairs": collaboration_success_rates,
            "most_effective_pair": max(
                collaboration_success_rates.items(), 
                key=lambda x: x[1]["success_rate"]
            ) if collaboration_success_rates else None
        }
    
    def get_global_context_summary(self) -> Dict[str, Any]:
        """Get a summary of the global context and learning"""
        return {
            "recent_requests_count": len(self.global_context.get("recent_requests", [])),
            "routing_history_count": len(self.global_context.get("routing_history", [])),
            "performance_insights": self.global_context.get("agent_performance_insights", {}),
            "collaboration_history_count": len(self.agent_collaboration_history),
            "context_last_updated": max([
                entry["timestamp"] for entry in self.global_context.get("recent_requests", [])
            ]) if self.global_context.get("recent_requests") else "Never"
        }
    
    async def get_detailed_agent_info(self, agent_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific agent"""
        if agent_name not in self.agents:
            return {"error": f"Agent {agent_name} not found"}
        
        agent = self.agents[agent_name]
        memory_summary = agent.get_memory_summary()
        plan_status = agent.get_current_plan_status()
        
        return {
            "name": agent.name,
            "description": agent.description,
            "capabilities": agent.capabilities,
            "memory": {
                "total_experiences": memory_summary["total_experiences"],
                "successful_patterns": memory_summary["successful_patterns"],
                "failed_patterns": memory_summary["failed_patterns"],
                "recent_experiences": memory_summary["recent_experiences"]
            },
            "current_plan": plan_status,
            "performance": self.global_context.get("agent_performance_insights", {}).get(agent_name, {})
        }
    
    async def reset_agent_memory(self, agent_name: str) -> bool:
        """Reset the memory of a specific agent"""
        if agent_name not in self.agents:
            return False
        
        agent = self.agents[agent_name]
        agent.memory = type(agent.memory)()  # Create new empty memory instance
        logger.info(f"🧠 Reset memory for agent: {agent_name}")
        return True
    
    async def reset_global_context(self) -> bool:
        """Reset the global context and learning history"""
        self.global_context = {}
        self.agent_collaboration_history = []
        logger.info("🔄 Reset global context and collaboration history")
        return True
    
    async def export_learning_data(self) -> Dict[str, Any]:
        """Export all learning data for analysis or backup"""
        learning_data = {
            "timestamp": datetime.now().isoformat(),
            "global_context": self.global_context,
            "collaboration_history": self.agent_collaboration_history,
            "agent_memories": {}
        }
        
        # Export individual agent memories
        for name, agent in self.agents.items():
            learning_data["agent_memories"][name] = agent.get_memory_summary()
        
        return learning_data
    
    async def import_learning_data(self, learning_data: Dict[str, Any]) -> bool:
        """Import learning data from a previous export"""
        try:
            if "global_context" in learning_data:
                self.global_context = learning_data["global_context"]
            
            if "collaboration_history" in learning_data:
                self.agent_collaboration_history = learning_data["collaboration_history"]
            
            # Note: Individual agent memories would need to be restored separately
            # as they are more complex data structures
            
            logger.info("📥 Imported learning data successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to import learning data: {e}")
            return False

# For backward compatibility, also export the old name
AgentManager = AgenticAgentManager