"""
JSON extraction and validation utilities.
"""
import json
import logging

from typing import Dict, Optional, Any, List, Tuple

logger = logging.getLogger(__name__)

class JSONExtractor:
    """Utility class for extracting JSON from LLM responses"""
    
    @staticmethod
    def extract_json_from_text(text: str) -> Optional[Dict]:
        """Extract JSON from text response"""
        try:
            if text.startswith("Error"):
                return None
            
            # Find JSON in the response
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = text[json_start:json_end]
                return json.loads(json_str)
            else:
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None
        except Exception as e:
            logger.error(f"JSON extraction error: {e}")
            return None
    
    @staticmethod
    def validate_expense_data(data: Dict) -> bool:
        """Validate extracted expense data"""
        required_fields = ['items']
        
        if not all(field in data for field in required_fields):
            return False
        
        if not isinstance(data['items'], list) or len(data['items']) == 0:
            return False
        
        # Validate each item
        for item in data['items']:
            if not isinstance(item, dict) or 'name' not in item:
                return False
        
        return True
    
    @staticmethod
    def validate_json_structure(data: Dict, required_fields: List[str]) -> Tuple[bool, str]:
        """Validate JSON structure against required fields"""
        if not isinstance(data, dict):
            return False, "Data must be a dictionary"
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        return True, "Valid structure"
    
    @staticmethod
    def safe_extract_field(data: Dict, field: str, default: Any = None) -> Any:
        """Safely extract a field from dictionary with default"""
        try:
            return data.get(field, default)
        except (AttributeError, TypeError):
            return default
    
    @staticmethod
    def clean_json_response(text: str) -> str:
        """Clean common issues in LLM JSON responses"""
        # Remove markdown code blocks
        text = text.replace('```json', '').replace('```', '')
        
        # Remove common prefixes
        prefixes_to_remove = [
            'Here is the JSON:',
            'Here\'s the JSON:',
            'JSON:',
            'Result:',
            'Output:'
        ]
        
        for prefix in prefixes_to_remove:
            if text.strip().startswith(prefix):
                text = text.strip()[len(prefix):].strip()
        
        return text.strip()
    
    @staticmethod
    def prettify_json(data: Dict, indent: int = 2) -> str:
        """Pretty print JSON data"""
        try:
            return json.dumps(data, indent=indent, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to prettify JSON: {e}")
            return str(data)
    
    @staticmethod
    def merge_json_objects(obj1: Dict, obj2: Dict) -> Dict:
        """Merge two JSON objects, with obj2 taking precedence"""
        try:
            result = obj1.copy()
            result.update(obj2)
            return result
        except Exception as e:
            logger.error(f"Failed to merge JSON objects: {e}")
            return obj1