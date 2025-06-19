"""
Agentic Text Expense Processing Agent with natural language understanding and reasoning.
"""
import json
import logging
import re
from typing import Dict, Any, List
from datetime import datetime

from .base import AgenticBaseAgent, Task, TaskType, Plan
from src.models import AgentResult, JSONExtractor

logger = logging.getLogger(__name__)

class AgenticTextExpenseAgent(AgenticBaseAgent):
    """Advanced text expense processing agent with language understanding and reasoning"""
    
    def __init__(self):
        super().__init__(
            name="Agentic Text Expense Agent",
            description="Intelligently processes natural language expense text with contextual understanding",
            capabilities=[
                "natural_language_processing",
                "context_understanding",
                "intent_detection",
                "entity_extraction",
                "ambiguity_resolution",
                "multi_language_support",
                "conversation_tracking",
                "smart_categorization",
                "price_inference"
            ]
        )
    
    async def _perform_input_analysis(self, **kwargs) -> Dict[str, Any]:
        """Analyze text input and create detailed linguistic context"""
        analysis = {}
        
        if "text" in kwargs:
            text = kwargs["text"]
            
            # Basic text characteristics
            analysis.update(await self._analyze_text_characteristics(text))
            
            # Linguistic analysis
            analysis.update(await self._analyze_language_and_intent(text))
            
            # Context and complexity analysis
            analysis.update(await self._analyze_context_complexity(text))
        
        if "message_date" in kwargs:
            analysis["provided_date"] = kwargs["message_date"]
        
        # Determine processing strategy
        analysis["recommended_strategy"] = await self._determine_text_processing_strategy(analysis)
        
        return analysis
    
    async def _analyze_text_characteristics(self, text: str) -> Dict[str, Any]:
        """Analyze basic characteristics of the input text"""
        return {
            "text_length": len(text),
            "word_count": len(text.split()),
            "has_numbers": bool(re.search(r'\d', text)),
            "has_currency": bool(re.search(r'[₹$€£¥]|rupee|dollar|euro', text.lower())),
            "has_quantities": bool(re.search(r'\d+\s*(kg|g|litre|l|pcs|pieces|dozen)', text.lower())),
            "language_hints": self._detect_language_hints(text)
        }
    
    def _detect_language_hints(self, text: str) -> List[str]:
        """Detect language hints in the text"""
        hints = []
        
        # Hindi/Hinglish patterns
        hindi_patterns = [
            r'rupay|रुपय|रु\.|₹',
            r'kilo|किलो',
            r'sabzi|सब्जी',
            r'dukan|दुकान'
        ]
        
        for pattern in hindi_patterns:
            if re.search(pattern, text.lower()):
                hints.append("hindi_hinglish")
                break
        
        # English patterns
        if re.search(r'\b(bought|purchased|spent|cost|price|total)\b', text.lower()):
            hints.append("english")
        
        return hints if hints else ["english"]
    
    async def _analyze_language_and_intent(self, text: str) -> Dict[str, Any]:
        """Analyze language and user intent"""
        intent_prompt = f"""
        Analyze this text for language and intent:
        
        Text: "{text}"
        
        Determine:
        1. Primary language (english/hindi/hinglish/other)
        2. User intent (record_expense/ask_question/casual_chat/unclear)
        3. Confidence level (0.0-1.0)
        4. Communication style (formal/casual/abbreviated)
        5. Expense indicators found
        
        Respond with JSON:
        {{
            "language": "english|hindi|hinglish|other",
            "intent": "record_expense|ask_question|casual_chat|unclear", 
            "confidence": 0.8,
            "style": "formal|casual|abbreviated",
            "expense_indicators": ["currency_mentioned", "items_listed"],
            "ambiguity_level": "low|medium|high"
        }}
        """
        
        try:
            response = self.gemini_service.call(intent_prompt)
            intent_data = JSONExtractor.extract_json_from_text(response)
            
            if intent_data:
                return intent_data
            else:
                return {"language": "english", "intent": "unclear", "confidence": 0.5}
                
        except Exception as e:
            logger.warning(f"⚠️ Language analysis failed: {e}")
            return {"language": "english", "intent": "record_expense", "confidence": 0.3}
    
    async def _analyze_context_complexity(self, text: str) -> Dict[str, Any]:
        """Analyze context and complexity of the expense description"""
        complexity_prompt = f"""
        Analyze the complexity and context of this expense text:
        
        Text: "{text}"
        
        Evaluate:
        1. Information completeness (all_details/some_missing/very_incomplete)
        2. Ambiguity level (clear/somewhat_ambiguous/very_ambiguous)
        3. Multiple items mentioned (single/few/many)
        4. Price clarity (explicit/implicit/missing)
        5. Context richness (detailed/basic/minimal)
        
        Respond with JSON:
        {{
            "completeness": "all_details|some_missing|very_incomplete",
            "ambiguity": "clear|somewhat_ambiguous|very_ambiguous",
            "item_count": "single|few|many",
            "price_clarity": "explicit|implicit|missing",
            "context_richness": "detailed|basic|minimal",
            "processing_complexity": "simple|moderate|complex"
        }}
        """
        
        try:
            response = self.gemini_service.call(complexity_prompt)
            complexity_data = JSONExtractor.extract_json_from_text(response)
            
            if complexity_data:
                return complexity_data
            else:
                return {"processing_complexity": "moderate"}
                
        except Exception as e:
            logger.warning(f"⚠️ Complexity analysis failed: {e}")
            return {"processing_complexity": "moderate"}
    
    async def _determine_text_processing_strategy(self, analysis: Dict[str, Any]) -> str:
        """Determine the best text processing strategy"""
        intent = analysis.get("intent", "unclear")
        complexity = analysis.get("processing_complexity", "moderate")
        ambiguity = analysis.get("ambiguity", "clear")
        completeness = analysis.get("completeness", "some_missing")
        
        # Strategy selection based on analysis
        if intent != "record_expense":
            return "intent_clarification"
        elif ambiguity == "very_ambiguous" or completeness == "very_incomplete":
            return "conversational_clarification"
        elif complexity == "complex":
            return "multi_step_extraction"
        else:
            return "direct_extraction"
    
    async def execute_reasoning_task(self, task: Task, context: Dict[str, Any]) -> AgentResult:
        """Execute reasoning-based tasks for text processing"""
        try:
            if task.type == TaskType.ANALYZE:
                return await self._execute_text_analysis_task(task, context)
            elif task.type == TaskType.REASON:
                return await self._execute_text_reasoning_task(task, context)
            elif task.type == TaskType.VALIDATE:
                return await self._execute_text_validation_task(task, context)
            else:
                return AgentResult(
                    success=False,
                    message=f"Unknown reasoning task type: {task.type}",
                    error="Unsupported task type"
                )
        except Exception as e:
            logger.error(f"❌ Text reasoning task failed: {e}")
            return AgentResult(
                success=False,
                message=f"Text reasoning task failed: {task.description}",
                error=str(e)
            )
    
    async def _execute_text_analysis_task(self, task: Task, context: Dict[str, Any]) -> AgentResult:
        """Execute text analysis tasks"""
        if "analyze_expense_entities" in task.description:
            text = context.get("input_data", {}).get("text", "")
            
            entity_prompt = f"""
            Extract and analyze entities from this expense text:
            
            Text: "{text}"
            
            Identify:
            1. Items/products mentioned
            2. Quantities and units
            3. Prices and currency
            4. Store/vendor names
            5. Time references
            6. Location references
            
            For each entity, provide:
            - Type (item/quantity/price/store/time/location)
            - Value extracted
            - Confidence level
            - Position in text
            
            Respond with structured entity analysis.
            """
            
            try:
                response = self.gemini_service.call(entity_prompt)
                entity_data = JSONExtractor.extract_json_from_text(response)
                
                return AgentResult(
                    success=True,
                    message="Text entities analyzed",
                    data={"entities": entity_data}
                )
            except Exception as e:
                return AgentResult(
                    success=False,
                    message="Entity analysis failed",
                    error=str(e)
                )
        
        return AgentResult(
            success=True,
            message=f"Text analysis completed: {task.description}",
            data={}
        )
    
    async def _execute_text_reasoning_task(self, task: Task, context: Dict[str, Any]) -> AgentResult:
        """Execute reasoning tasks for text understanding"""
        if "resolve_ambiguities" in task.description:
            text = context.get("input_data", {}).get("text", "")
            entities = task.parameters.get("entities", {})
            
            reasoning_prompt = f"""
            Resolve ambiguities in this expense text using context and reasoning:
            
            Original Text: "{text}"
            Extracted Entities: {json.dumps(entities, indent=2)}
            
            Apply reasoning to:
            1. Infer missing prices from context
            2. Resolve unclear quantities  
            3. Determine implicit items
            4. Calculate totals when missing
            5. Standardize units and formats
            
            Use common sense about:
            - Typical grocery prices
            - Standard package sizes
            - Common shopping patterns
            - Regional pricing norms
            
            Provide reasoned conclusions with confidence levels.
            """
            
            try:
                response = self.gemini_service.call(reasoning_prompt)
                
                return AgentResult(
                    success=True,
                    message="Ambiguities resolved through reasoning",
                    data={"reasoning_result": response}
                )
            except Exception as e:
                return AgentResult(
                    success=False,
                    message="Ambiguity resolution failed",
                    error=str(e)
                )
        
        elif "infer_missing_information" in task.description:
            text = context.get("input_data", {}).get("text", "")
            
            inference_prompt = f"""
            Infer missing information from this expense text using context clues:
            
            Text: "{text}"
            
            Infer:
            1. Missing prices (use typical market prices)
            2. Missing quantities (use common purchase amounts)
            3. Missing units (kg/pcs based on item type)
            4. Likely store type
            5. Purchase date (if not specified)
            
            Base inferences on:
            - Common grocery shopping patterns
            - Typical pricing for mentioned items
            - Standard package sizes
            - Cultural/regional context
            
            Clearly mark inferred vs. explicit information.
            """
            
            try:
                response = self.gemini_service.call(inference_prompt)
                
                return AgentResult(
                    success=True,
                    message="Missing information inferred",
                    data={"inference_result": response}
                )
            except Exception as e:
                return AgentResult(
                    success=False,
                    message="Information inference failed",
                    error=str(e)
                )
        
        return AgentResult(
            success=True,
            message=f"Text reasoning completed: {task.description}",
            data={}
        )
    
    async def _execute_text_validation_task(self, task: Task, context: Dict[str, Any]) -> AgentResult:
        """Execute validation tasks for extracted text data"""
        extracted_data = task.parameters.get("data")
        
        validation_prompt = f"""
        Validate this extracted text expense data for logical consistency:
        
        Original Text: "{context.get('input_data', {}).get('text', '')}"
        Extracted Data: {json.dumps(extracted_data, indent=2)}
        
        Validate:
        1. Do prices seem reasonable for the items?
        2. Are quantities logical for typical purchases?
        3. Do units match the item types?
        4. Is the total calculation correct?
        5. Are item names properly formatted?
        6. Does the data match the original text intent?
        
        Respond with validation results:
        {{
            "is_valid": true/false,
            "confidence": 0.0-1.0,
            "price_reasonableness": "reasonable|too_high|too_low",
            "quantity_logic": "logical|questionable|illogical",
            "unit_consistency": "consistent|inconsistent",
            "total_accuracy": "correct|incorrect|missing",
            "issues": ["list of specific issues"],
            "suggestions": ["suggestions for improvements"]
        }}
        """
        
        try:
            response = self.gemini_service.call(validation_prompt)
            validation_data = JSONExtractor.extract_json_from_text(response)
            
            return AgentResult(
                success=True,
                message="Text data validation completed",
                data={"validation": validation_data}
            )
        except Exception as e:
            return AgentResult(
                success=False,
                message="Text validation failed",
                error=str(e)
            )
    
    async def synthesize_results(self, results: List[AgentResult], plan: Plan, 
                                context: Dict[str, Any]) -> AgentResult:
        """Synthesize all text processing results"""
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]
        
        if not successful_results:
            return AgentResult(
                success=False,
                message="All text processing tasks failed",
                error="No successful task results to synthesize"
            )
        
        # Extract data from results
        extracted_data = None
        validation_result = None
        reasoning_data = {}
        entity_data = {}
        
        for result in successful_results:
            if result.data:
                # Look for main extraction result
                if "items" in str(result.data):
                    try:
                        if isinstance(result.data, dict) and "expense_data" in result.data:
                            extracted_data = json.loads(result.data["expense_data"])
                        elif "task_result" in result.data:
                            extracted_data = JSONExtractor.extract_json_from_text(result.data["task_result"])
                    except:
                        pass
                
                if "validation" in result.data:
                    validation_result = result.data["validation"]
                
                if "entities" in result.data:
                    entity_data = result.data["entities"]
                
                if "reasoning_result" in result.data or "inference_result" in result.data:
                    reasoning_data.update(result.data)
        
        # Create comprehensive result
        if extracted_data:
            items_count = len(extracted_data.get('items', []))
            total = extracted_data.get('total', 'N/A')
            
            # Include processing insights
            strategy = context.get("recommended_strategy", "direct_extraction")
            language = context.get("language", "english")
            intent_confidence = context.get("confidence", 0.8)
            
            # Include validation information
            validation_info = ""
            if validation_result:
                confidence = validation_result.get("confidence", 0.8)
                price_reasonableness = validation_result.get("price_reasonableness", "reasonable")
                issues = validation_result.get("issues", [])
                
                if issues:
                    validation_info = f"\n⚠️ Issues: {', '.join(issues)}"
                else:
                    validation_info = f"\n✅ Validated (confidence: {confidence:.2f}, prices: {price_reasonableness})"
            
            success_message = (
                f"🤖 **Agentic Text Processing Complete!**\n\n"
                f"📅 Date: {context.get('provided_date', datetime.now().strftime('%Y-%m-%d'))}\n"
                f"📝 Items: {items_count}\n"
                f"💰 Total: ₹{total}\n"
                f"🗣️ Language: {language}\n"
                f"🎯 Strategy: {strategy}\n"
                f"🎯 Intent Confidence: {intent_confidence:.2f}{validation_info}\n"
                f"🧠 Plan executed with {len(plan.tasks)} tasks"
            )
            
            return AgentResult(
                success=True,
                message=success_message,
                data={
                    "extracted_data": extracted_data,
                    "processing_strategy": strategy,
                    "validation": validation_result,
                    "entities": entity_data,
                    "reasoning": reasoning_data,
                    "language_analysis": {
                        "language": language,
                        "intent_confidence": intent_confidence
                    },
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
                message="Text processing completed but no valid expense data extracted",
                error="Failed to extract structured expense data from text"
            )