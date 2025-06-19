"""
Service factory for dependency injection and service management.
"""
import logging

from typing import Dict, Any, TypeVar, Type
from .base import BaseService
from .gemini import GeminiService
from .google_sheets import GoogleSheetsService
from .prompts import PromptService

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseService)

class ServiceFactory:
    """Factory for creating and managing service instances"""
    
    def __init__(self):
        self._services: Dict[Type[BaseService], BaseService] = {}
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize all default services"""
        if self._initialized:
            return
        
        try:
            # Initialize singleton services
            self._services[GeminiService] = GeminiService()
            self._services[GoogleSheetsService] = GoogleSheetsService()
            self._services[PromptService] = PromptService()
            
            self._initialized = True
            logger.info("🏭 Service Factory initialized with all services")
            
        except Exception as e:
            logger.error(f"❌ Service Factory initialization failed: {e}")
            raise
    
    def get_service(self, service_type: Type[T]) -> T:
        """Get a service instance by type"""
        if not self._initialized:
            self.initialize()
        
        service = self._services.get(service_type)
        if not service:
            raise ValueError(f"Service {service_type.__name__} not registered")
        
        return service # type: ignore
    
    def register_service(self, service_type: Type[T], service_instance: T) -> None:
        """Register a custom service instance"""
        self._services[service_type] = service_instance
        logger.info(f"📋 Registered service: {service_type.__name__}")
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Run health checks on all services"""
        if not self._initialized:
            self.initialize()
        
        results = {}
        for service_type, service in self._services.items():
            try:
                if hasattr(service, 'health_check'):
                    results[service_type.__name__] = await service.health_check()
                else:
                    results[service_type.__name__] = True  # Assume healthy if no check
            except Exception as e:
                logger.error(f"Health check failed for {service_type.__name__}: {e}")
                results[service_type.__name__] = False
        
        return results
    
    def get_service_status(self) -> Dict[str, str]:
        """Get status of all registered services"""
        if not self._initialized:
            return {"status": "Not initialized"}
        
        status = {}
        for service_type, service in self._services.items():
            status[service_type.__name__] = "✅ Registered"
        
        return status

# Global service factory instance
service_factory = ServiceFactory()