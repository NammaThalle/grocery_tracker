"""
Simplified Agentic Receipt Processing Agent - focuses on OCR with intelligent planning.
"""
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

from .base import AgenticBaseAgent, Task, TaskType, Plan
from src.models import AgentResult, JSONExtractor

logger = logging.getLogger(__name__)

class AgenticReceiptProcessingAgent(AgenticBaseAgent):
    """Simplified agentic receipt processing agent focused on intelligent OCR"""
    
    def __init__(self):
        super().__init__(
            name="Agentic Receipt Processing Agent",
            description="Intelligently processes receipt images with dynamic planning",
            capabilities=[
                "receipt_ocr",
                "data_extraction", 
                "intelligent_planning",
                "error_recovery"
            ]
        )
    
    async def _perform_input_analysis(self, **kwargs) -> Dict[str, Any]:
        """Simple input analysis without complex image processing"""
        analysis = {
            "has_image": "image_data" in kwargs,
            "has_date": "message_date" in kwargs,
            "processing_approach": "direct_ocr"
        }
        
        if "message_date" in kwargs:
            analysis["provided_date"] = kwargs["message_date"]
        
        return analysis
    
    async def execute_reasoning_task(self, task: Task, context: Dict[str, Any]) -> AgentResult:
        """Execute simple reasoning tasks"""
        if task.type == TaskType.REASON:
            return AgentResult(
                success=True,
                message=f"Reasoning completed: {task.description}",
                data={"reasoning": "Simple OCR approach selected"}
            )
        else:
            return AgentResult(
                success=True,
                message=f"Task completed: {task.description}",
                data={}
            )
    
    async def synthesize_results(self, results: List[AgentResult], plan: Plan, 
                                context: Dict[str, Any]) -> AgentResult:
        """Synthesize receipt processing results"""
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]
        
        if not successful_results:
            return AgentResult(
                success=False,
                message="Receipt processing failed - no successful tasks",
                error="All tasks failed"
            )
        
        # Find the main OCR result and save result
        extracted_data = None
        save_result = None
        items_count = 0
        
        for result in successful_results:
            # Check if this is a save result
            if "Successfully saved" in result.message or "Added" in result.message:
                save_result = result.message
                # Try to extract item count from save message
                import re
                match = re.search(r'(\d+)', result.message)
                if match:
                    items_count = int(match.group(1))
            
            # Check if this has task_result with JSON data
            if result.data and "task_result" in result.data:
                try:
                    task_result = result.data["task_result"]
                    if isinstance(task_result, str) and not task_result.startswith("Error"):
                        # Try to parse as JSON directly first
                        import json
                        try:
                            extracted_data = json.loads(task_result)
                        except json.JSONDecodeError:
                            # Try to extract JSON from the string using JSONExtractor
                            extracted_data = JSONExtractor.extract_json_from_text(task_result)
                        
                        if extracted_data:
                            break  # Found valid data, stop looking
                            
                except Exception as e:
                    logger.warning(f"⚠️ Failed to parse task result: {e}")
                    continue
        
        # Create detailed result like the old system
        if extracted_data and isinstance(extracted_data, dict):
            # Extract receipt details
            items_list = extracted_data.get('items', [])
            items_count = len(items_list) if items_list else items_count
            total = extracted_data.get('total', extracted_data.get('subtotal', 'N/A'))
            store = extracted_data.get('store', 'Unknown')
            receipt_date = extracted_data.get('date', 'N/A')
            
            # Format the success message like the old system
            success_message = (
                f"✅ Receipt processed successfully!\n\n"
                f"📅 Date: {receipt_date if receipt_date != 'N/A' else context.get('provided_date', 'N/A')}\n"
                f"🏪 Store: {store}\n"
                f"📝 Items: {items_count}\n"
                f"💰 Total: ₹{total}"
            )
            
            if save_result:
                success_message += f"\n📊 {save_result}"
            
            return AgentResult(
                success=True,
                message=success_message,
                data={
                    "extracted_data": extracted_data,
                    "processing_strategy": "simple_agentic_ocr",
                    "items_processed": items_count,
                    "plan_summary": {
                        "total_tasks": len(plan.tasks),
                        "successful_tasks": len(successful_results),
                        "failed_tasks": len(failed_results)
                    }
                }
            )
        
        # Fallback if we have save result but no detailed data
        elif save_result and items_count > 0:
            success_message = (
                f"✅ Receipt processed successfully!\n\n"
                f"📅 Date: {context.get('provided_date', 'N/A')}\n"
                f"🏪 Store: Unknown\n"
                f"📝 Items: {items_count}\n"
                f"💰 Total: N/A\n"
                f"📊 {save_result}"
            )
            
            return AgentResult(
                success=True,
                message=success_message,
                data={
                    "processing_strategy": "simple_agentic_ocr",
                    "items_processed": items_count,
                    "plan_summary": {
                        "total_tasks": len(plan.tasks),
                        "successful_tasks": len(successful_results),
                        "failed_tasks": len(failed_results)
                    }
                }
            )
        
        # If we have successful results but no clear save result, still report success
        elif successful_results:
            return AgentResult(
                success=True,
                message=f"✅ Agentic processing completed with {len(successful_results)} successful tasks",
                data={
                    "processing_strategy": "simple_agentic_ocr",
                    "plan_summary": {
                        "total_tasks": len(plan.tasks),
                        "successful_tasks": len(successful_results),
                        "failed_tasks": len(failed_results)
                    }
                }
            )
        else:
            return AgentResult(
                success=False,
                message="Receipt processing completed but no valid data extracted",
                error="Failed to extract structured data from receipt"
            )