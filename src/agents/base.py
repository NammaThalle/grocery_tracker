"""
Base agent class for the Agentic AI Grocery Bot system.
Enhanced with reasoning, planning, and dynamic decision-making capabilities.
"""
import json
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from src.models import AgentResult
from src.tools import ToolRegistry
from src.services import GeminiService

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Types of tasks an agent can handle"""
    ANALYZE = "analyze"
    EXTRACT = "extract"
    PROCESS = "process"
    SAVE = "save"
    VALIDATE = "validate"
    REASON = "reason"

@dataclass
class Task:
    """Represents a single task in an agent's plan"""
    id: str
    type: TaskType
    description: str
    tool_name: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, running, completed, failed
    result: Any = None
    confidence: float = 1.0

@dataclass
class Plan:
    """Represents an execution plan with multiple tasks"""
    id: str
    goal: str
    tasks: List[Task] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "created"  # created, executing, completed, failed
    
    def get_next_tasks(self) -> List[Task]:
        """Get tasks that are ready to execute"""
        ready_tasks = []
        completed_task_ids = {task.id for task in self.tasks if task.status == "completed"}
        
        for task in self.tasks:
            if task.status == "pending":
                # Check if all dependencies are completed
                if all(dep_id in completed_task_ids for dep_id in task.dependencies):
                    ready_tasks.append(task)
        
        return ready_tasks
    
    def is_complete(self) -> bool:
        """Check if all tasks are completed"""
        return all(task.status in ["completed", "skipped"] for task in self.tasks)
    
    def has_failed(self) -> bool:
        """Check if any critical task has failed"""
        return any(task.status == "failed" for task in self.tasks)

@dataclass
class AgentMemory:
    """Memory system for agents to learn from past interactions"""
    experiences: List[Dict[str, Any]] = field(default_factory=list)
    successful_patterns: Dict[str, int] = field(default_factory=dict)
    failed_patterns: Dict[str, int] = field(default_factory=dict)
    context_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def remember_experience(self, context: Dict[str, Any], plan: Plan, result: AgentResult):
        """Store an experience for future learning"""
        experience = {
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "plan_id": plan.id,
            "goal": plan.goal,
            "tasks_count": len(plan.tasks),
            "success": result.success,
            "result": result.message if result.success else result.error
        }
        self.experiences.append(experience)
        
        # Update pattern tracking
        pattern_key = f"{plan.goal}_{len(plan.tasks)}_tasks"
        if result.success:
            self.successful_patterns[pattern_key] = self.successful_patterns.get(pattern_key, 0) + 1
        else:
            self.failed_patterns[pattern_key] = self.failed_patterns.get(pattern_key, 0) + 1
    
    def get_similar_experiences(self, context: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar past experiences for learning"""
        # Simple similarity based on context keys (can be enhanced with embeddings)
        context_keys = set(context.keys())
        similar_experiences = []
        
        for exp in self.experiences:
            exp_keys = set(exp["context"].keys())
            similarity = len(context_keys.intersection(exp_keys)) / len(context_keys.union(exp_keys))
            if similarity > 0.3:  # Threshold for similarity
                similar_experiences.append((similarity, exp))
        
        # Sort by similarity and return top results
        similar_experiences.sort(key=lambda x: x[0], reverse=True)
        return [exp for _, exp in similar_experiences[:limit]]

class AgenticBaseAgent(ABC):
    """Enhanced base class for all agentic agents with reasoning capabilities"""
    
    def __init__(self, name: str, description: str, capabilities: List[str]):
        self.name = name
        self.description = description
        self.capabilities = capabilities  # What this agent can do
        self.tool_registry = ToolRegistry()
        self.gemini_service = GeminiService()
        self.memory = AgentMemory()
        self.current_plan: Optional[Plan] = None
        logger.info(f"🤖 Initialized agentic agent: {name}")
    
    async def execute(self, **kwargs) -> AgentResult:
        """Main execution method with agentic capabilities"""
        try:
            # Step 1: Analyze the input and create context
            context = await self.analyze_input(**kwargs)
            logger.info(f"🔍 {self.name} analyzed input: {list(context.keys())}")
            
            # Step 2: Create a goal-oriented plan
            plan = await self.create_plan(context)
            self.current_plan = plan
            logger.info(f"📋 {self.name} created plan with {len(plan.tasks)} tasks")
            
            # Step 3: Execute the plan dynamically
            result = await self.execute_plan(plan, context)
            
            # Step 4: Learn from the experience
            self.memory.remember_experience(context, plan, result)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ {self.name} execution failed: {e}")
            return AgentResult(
                success=False,
                message=f"Agent execution failed: {str(e)}",
                error=str(e)
            )
    
    async def analyze_input(self, **kwargs) -> Dict[str, Any]:
        """Analyze input and create context for planning"""
        context = {
            "input_type": self._determine_input_type(**kwargs),
            "input_data": kwargs,
            "timestamp": datetime.now().isoformat(),
            "agent_name": self.name
        }
        
        # Add input-specific analysis
        context.update(await self._perform_input_analysis(**kwargs))
        
        return context
    
    async def create_plan(self, context: Dict[str, Any]) -> Plan:
        """Create an execution plan based on context and goals"""
        # Check memory for similar successful experiences
        similar_experiences = self.memory.get_similar_experiences(context)
        
        # Use AI to create a smart plan
        planning_prompt = self._get_planning_prompt(context, similar_experiences)
        planning_response = await self._call_planning_ai(planning_prompt)
        
        # Parse the AI response into a structured plan
        plan = await self._parse_plan_response(planning_response, context)
        
        return plan
    
    async def execute_plan(self, plan: Plan, context: Dict[str, Any]) -> AgentResult:
        """Execute the plan dynamically with adaptation"""
        plan.status = "executing"
        results = []
        
        # Check if plan has tasks
        if not plan.tasks:
            logger.warning("⚠️ Plan has no tasks, creating fallback execution")
            return await self._execute_fallback_processing(context)
        
        while not plan.is_complete() and not plan.has_failed():
            # Get next available tasks
            ready_tasks = plan.get_next_tasks()
            
            if not ready_tasks:
                logger.warning(f"⚠️ No ready tasks found, checking for deadlock")
                break
            
            # Execute ready tasks (can be parallel in future)
            for task in ready_tasks:
                task_result = await self.execute_task(task, context)
                results.append(task_result)
                
                # Adapt plan if needed based on task result
                if not task_result.success:
                    adapted_plan = await self.adapt_plan(plan, task, task_result, context)
                    if adapted_plan:
                        plan = adapted_plan
                        self.current_plan = plan
        
        # Synthesize final result
        final_result = await self.synthesize_results(results, plan, context)
        plan.status = "completed" if final_result.success else "failed"
        
        return final_result
    
    async def _execute_fallback_processing(self, context: Dict[str, Any]) -> AgentResult:
        """Execute fallback processing when planning fails"""
        input_type = context.get("input_type", "unknown")
        
        try:
            if input_type == "image":
                # Direct image processing
                image_data = context.get("input_data", {}).get("image_data")
                if image_data:
                    result = await self._execute_tool("process_receipt", image_data=image_data)
                    if not result.startswith("Error"):
                        save_result = await self._execute_tool("save_to_sheets", expense_data=result)
                        return AgentResult(
                            success=True,
                            message=f"✅ Fallback processing completed\n📊 {save_result}",
                            data={"fallback_used": True}
                        )
            
            elif input_type == "text":
                # Direct text processing
                text = context.get("input_data", {}).get("text")
                if text:
                    result = await self._execute_tool("extract_text_expense", text=text)
                    if not result.startswith("Error"):
                        save_result = await self._execute_tool("save_to_sheets", expense_data=result)
                        return AgentResult(
                            success=True,
                            message=f"✅ Fallback processing completed\n📊 {save_result}",
                            data={"fallback_used": True}
                        )
            
            return AgentResult(
                success=False,
                message="Fallback processing failed",
                error="No suitable fallback strategy found"
            )
            
        except Exception as e:
            logger.error(f"❌ Fallback processing failed: {e}")
            return AgentResult(
                success=False,
                message="Fallback processing failed",
                error=str(e)
            )
    
    async def execute_task(self, task: Task, context: Dict[str, Any]) -> AgentResult:
        """Execute a single task"""
        task.status = "running"
        logger.info(f"⚙️ Executing task: {task.description}")
        
        try:
            if task.tool_name:
                # Get the required parameters from context
                tool_params = {}
                
                if task.tool_name == "process_receipt":
                    image_data = context.get("input_data", {}).get("image_data")
                    if image_data:
                        tool_params["image_data"] = image_data
                
                elif task.tool_name == "extract_text_expense":
                    text = context.get("input_data", {}).get("text")
                    if text:
                        tool_params["text"] = text
                
                elif task.tool_name == "save_to_sheets":
                    # Get data from previous task results
                    message_date = context.get("input_data", {}).get("message_date")
                    if message_date:
                        tool_params["message_date"] = message_date
                    
                    # Look for expense data from previous tasks
                    for prev_task in getattr(self.current_plan, 'tasks', []):
                        if prev_task.status == "completed" and prev_task.result:
                            if isinstance(prev_task.result, str) and not prev_task.result.startswith("Error"):
                                tool_params["expense_data"] = prev_task.result
                                break
                
                # Add any additional parameters from task
                tool_params.update(task.parameters)
                
                # Execute using specified tool
                tool_result = await self.tool_registry.execute_tool(
                    task.tool_name, 
                    **tool_params
                )
                
                if tool_result.startswith("Error"):
                    task.status = "failed"
                    return AgentResult(
                        success=False,
                        message=f"Task failed: {task.description}",
                        error=tool_result
                    )
                else:
                    task.status = "completed"
                    task.result = tool_result
                    return AgentResult(
                        success=True,
                        message=f"Task completed: {task.description}",
                        data={"task_result": tool_result}
                    )
            else:
                # Execute using agent's own reasoning
                result = await self.execute_reasoning_task(task, context)
                task.status = "completed" if result.success else "failed"
                task.result = result.data
                return result
                
        except Exception as e:
            task.status = "failed"
            logger.error(f"❌ Task execution failed: {e}")
            return AgentResult(
                success=False,
                message=f"Task execution failed: {task.description}",
                error=str(e)
            )
    
    async def adapt_plan(self, plan: Plan, failed_task: Task, error_result: AgentResult, 
                        context: Dict[str, Any]) -> Optional[Plan]:
        """Adapt the plan when a task fails"""
        logger.info(f"🔄 Adapting plan due to failed task: {failed_task.description}")
        
        # Use AI to determine how to adapt
        adaptation_prompt = f"""
        A task in my plan has failed. Help me adapt:
        
        Original Goal: {plan.goal}
        Failed Task: {failed_task.description}
        Error: {error_result.error}
        
        Available tools: {list(self.tool_registry.list_tools().keys())}
        Agent capabilities: {self.capabilities}
        
        How should I modify my plan? Consider:
        1. Alternative tools or approaches
        2. Breaking the task into smaller steps
        3. Changing the order of operations
        4. Adding validation or preprocessing steps
        
        Respond with a new plan in JSON format.
        """
        
        try:
            adaptation_response = self.gemini_service.call(adaptation_prompt)
            adapted_plan = await self._parse_plan_response(adaptation_response, context)
            adapted_plan.id = f"{plan.id}_adapted_{datetime.now().strftime('%H%M%S')}"
            
            logger.info(f"✅ Plan adapted with {len(adapted_plan.tasks)} tasks")
            return adapted_plan
            
        except Exception as e:
            logger.error(f"❌ Plan adaptation failed: {e}")
            return None
    
    # Abstract methods for subclasses to implement
    @abstractmethod
    async def _perform_input_analysis(self, **kwargs) -> Dict[str, Any]:
        """Perform agent-specific input analysis"""
        pass
    
    @abstractmethod
    async def execute_reasoning_task(self, task: Task, context: Dict[str, Any]) -> AgentResult:
        """Execute tasks that require agent-specific reasoning"""
        pass
    
    @abstractmethod
    async def synthesize_results(self, results: List[AgentResult], plan: Plan, 
                                context: Dict[str, Any]) -> AgentResult:
        """Synthesize multiple task results into final result"""
        pass
    
    # Helper methods
    def _determine_input_type(self, **kwargs) -> str:
        """Determine the type of input received"""
        if "image_data" in kwargs:
            return "image"
        elif "text" in kwargs:
            return "text"
        else:
            return "unknown"
    
    def _get_planning_prompt(self, context: Dict[str, Any], 
                           similar_experiences: List[Dict[str, Any]]) -> str:
        """Generate a simple, focused prompt for planning"""
        input_type = context.get("input_type", "unknown")
        
        if input_type == "image":
            base_prompt = f"""
            Create a simple plan to process a receipt image:
            
            Agent: {self.name}
            Available Tools: {list(self.tool_registry.list_tools().keys())}
            
            Create a plan with 2-3 tasks maximum:
            1. Extract data from receipt image
            2. Save data to Google Sheets
            3. (Optional) Validate results
            
            Respond with this exact JSON format:
            {{
                "goal": "Extract receipt data and save to sheets",
                "tasks": [
                    {{
                        "id": "extract_data",
                        "type": "extract",
                        "description": "Extract expense data from receipt image",
                        "tool_name": "process_receipt",
                        "parameters": {{}},
                        "dependencies": [],
                        "confidence": 0.9
                    }},
                    {{
                        "id": "save_data",
                        "type": "save", 
                        "description": "Save extracted data to Google Sheets",
                        "tool_name": "save_to_sheets",
                        "parameters": {{}},
                        "dependencies": ["extract_data"],
                        "confidence": 0.9
                    }}
                ]
            }}
            """
        elif input_type == "text":
            base_prompt = f"""
            Create a simple plan to process expense text:
            
            Agent: {self.name}
            Available Tools: {list(self.tool_registry.list_tools().keys())}
            
            Create a plan with 2 tasks:
            1. Extract data from text
            2. Save data to Google Sheets
            
            Respond with this exact JSON format:
            {{
                "goal": "Extract text expense data and save to sheets",
                "tasks": [
                    {{
                        "id": "extract_data",
                        "type": "extract",
                        "description": "Extract expense data from text",
                        "tool_name": "extract_text_expense",
                        "parameters": {{}},
                        "dependencies": [],
                        "confidence": 0.9
                    }},
                    {{
                        "id": "save_data",
                        "type": "save",
                        "description": "Save extracted data to Google Sheets", 
                        "tool_name": "save_to_sheets",
                        "parameters": {{}},
                        "dependencies": ["extract_data"],
                        "confidence": 0.9
                    }}
                ]
            }}
            """
        else:
            base_prompt = f"""
            Create a simple processing plan:
            
            Respond with JSON format with goal and tasks array.
            """
        
        return base_prompt
    
    async def _call_planning_ai(self, prompt: str) -> str:
        """Call AI service for planning"""
        try:
            response = self.gemini_service.call(prompt)
            if not response or response.strip() == "":
                logger.warning("⚠️ Empty response from Gemini service")
                return self._get_fallback_plan_json()
            
            if response.startswith("Error"):
                logger.warning(f"⚠️ Error response from Gemini: {response}")
                return self._get_fallback_plan_json()
            
            return response
        except Exception as e:
            logger.error(f"❌ Planning AI call failed: {e}")
            return self._get_fallback_plan_json()
    
    def _get_fallback_plan_json(self) -> str:
        """Get fallback plan JSON when AI planning fails"""
        return '''
        {
            "goal": "Process input using fallback strategy",
            "tasks": [
                {
                    "id": "task_1",
                    "type": "extract",
                    "description": "Extract data from input",
                    "tool_name": null,
                    "parameters": {},
                    "dependencies": [],
                    "confidence": 0.7
                }
            ]
        }
        '''
    
    async def _parse_plan_response(self, response: str, context: Dict[str, Any]) -> Plan:
        """Parse AI response into a structured plan"""
        try:
            if not response or response.strip() == "":
                logger.warning("⚠️ Empty response from planning AI")
                return self._create_fallback_plan(context)
            
            # Clean the response first
            cleaned_response = response.strip()
            
            # Extract JSON from response
            json_start = cleaned_response.find('{')
            json_end = cleaned_response.rfind('}') + 1
            
            if json_start == -1 or json_end <= json_start:
                logger.warning("⚠️ No JSON found in planning response")
                return self._create_fallback_plan(context)
            
            json_str = cleaned_response[json_start:json_end]
            plan_data = json.loads(json_str)
            
            # Create Plan object
            plan = Plan(
                id=f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                goal=plan_data.get("goal", "Process input intelligently"),
                context=context
            )
            
            # Create Task objects
            for task_data in plan_data.get("tasks", []):
                task = Task(
                    id=task_data.get("id", f"task_{len(plan.tasks) + 1}"),
                    type=TaskType(task_data.get("type", "process")),
                    description=task_data.get("description", "Process data"),
                    tool_name=task_data.get("tool_name"),
                    parameters=task_data.get("parameters", {}),
                    dependencies=task_data.get("dependencies", []),
                    confidence=task_data.get("confidence", 1.0)
                )
                plan.tasks.append(task)
            
            return plan
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing failed: {e}")
            return self._create_fallback_plan(context)
        except Exception as e:
            logger.error(f"❌ Plan parsing failed: {e}")
            return self._create_fallback_plan(context)
    
    def _create_fallback_plan(self, context: Dict[str, Any]) -> Plan:
        """Create a fallback plan when AI planning fails"""
        input_type = context.get("input_type", "unknown")
        
        plan = Plan(
            id=f"fallback_plan_{datetime.now().strftime('%H%M%S')}",
            goal="Process input using fallback strategy",
            context=context
        )
        
        if input_type == "image":
            # Fallback plan for image processing
            plan.tasks = [
                Task(
                    id="task_1",
                    type=TaskType.EXTRACT,
                    description="Extract data from receipt image",
                    tool_name="process_receipt",
                    parameters={"image_data": context.get("input_data", {}).get("image_data")},
                    dependencies=[],
                    confidence=0.8
                ),
                Task(
                    id="task_2", 
                    type=TaskType.SAVE,
                    description="Save extracted data to sheets",
                    tool_name="save_to_sheets",
                    parameters={},
                    dependencies=["task_1"],
                    confidence=0.9
                )
            ]
        elif input_type == "text":
            # Fallback plan for text processing
            plan.tasks = [
                Task(
                    id="task_1",
                    type=TaskType.EXTRACT,
                    description="Extract expense data from text",
                    tool_name="extract_text_expense",
                    parameters={"text": context.get("input_data", {}).get("text")},
                    dependencies=[],
                    confidence=0.8
                ),
                Task(
                    id="task_2",
                    type=TaskType.SAVE,
                    description="Save extracted data to sheets", 
                    tool_name="save_to_sheets",
                    parameters={},
                    dependencies=["task_1"],
                    confidence=0.9
                )
            ]
        else:
            # Generic fallback
            plan.tasks = [
                Task(
                    id="task_1",
                    type=TaskType.PROCESS,
                    description="Process input data",
                    tool_name=None,
                    parameters={},
                    dependencies=[],
                    confidence=0.5
                )
            ]
        
        logger.info(f"🔄 Created fallback plan with {len(plan.tasks)} tasks")
        return plan
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get a summary of agent's memory and learning"""
        return {
            "total_experiences": len(self.memory.experiences),
            "successful_patterns": self.memory.successful_patterns,
            "failed_patterns": self.memory.failed_patterns,
            "recent_experiences": self.memory.experiences[-5:] if self.memory.experiences else []
        }
    
    def get_current_plan_status(self) -> Optional[Dict[str, Any]]:
        """Get status of current plan execution"""
        if not self.current_plan:
            return None
        
        return {
            "plan_id": self.current_plan.id,
            "goal": self.current_plan.goal,
            "status": self.current_plan.status,
            "total_tasks": len(self.current_plan.tasks),
            "completed_tasks": len([t for t in self.current_plan.tasks if t.status == "completed"]),
            "failed_tasks": len([t for t in self.current_plan.tasks if t.status == "failed"]),
            "progress": len([t for t in self.current_plan.tasks if t.status == "completed"]) / len(self.current_plan.tasks) if self.current_plan.tasks else 0
        }