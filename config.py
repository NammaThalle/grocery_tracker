"""
Configuration management for the Grocery Bot system.
Enhanced version with better validation, environment handling, and modular support.
"""
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup logger for configuration
logger = logging.getLogger(__name__)

def singleton(cls):
    """Singleton decorator for ensuring single instance"""
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
@dataclass
class Config:
    """
    System configuration - Singleton to ensure consistent config across modules.
    Enhanced with better validation, defaults, and environment handling.
    """
    
    # ============================================================================
    # TELEGRAM CONFIGURATION
    # ============================================================================
    telegram_token: str = field(default_factory=lambda: os.getenv('TELEGRAM_BOT_TOKEN', ''))
    
    # ============================================================================
    # GEMINI AI CONFIGURATION  
    # ============================================================================
    gemini_api_key: str = field(default_factory=lambda: os.getenv('GEMINI_API_KEY', ''))
    gemini_model: str = field(default_factory=lambda: os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp'))
    gemini_temperature: float = field(default_factory=lambda: float(os.getenv('GEMINI_TEMPERATURE', '0.1')))
    gemini_max_tokens: int = field(default_factory=lambda: int(os.getenv('GEMINI_MAX_TOKENS', '8192')))
    
    # ============================================================================
    # GOOGLE SHEETS CONFIGURATION
    # ============================================================================
    sheets_credentials_path: str = field(default_factory=lambda: os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH', './credentials/google_credentials.json'))
    sheets_id: str = field(default_factory=lambda: os.getenv('GOOGLE_SHEETS_ID', ''))
    sheets_range: str = field(default_factory=lambda: os.getenv('SHEETS_RANGE', 'Sheet1!A:H'))
    sheets_batch_size: int = field(default_factory=lambda: int(os.getenv('SHEETS_BATCH_SIZE', '100')))
    
    # ============================================================================
    # APPLICATION SETTINGS
    # ============================================================================
    log_level: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))
    max_image_size: int = field(default_factory=lambda: int(os.getenv('MAX_IMAGE_SIZE', '4194304')))  # 4MB
    max_retries: int = field(default_factory=lambda: int(os.getenv('MAX_RETRIES', '3')))
    retry_delay: float = field(default_factory=lambda: float(os.getenv('RETRY_DELAY', '1.0')))
    
    # ============================================================================
    # AGENT SETTINGS
    # ============================================================================
    agent_timeout: int = field(default_factory=lambda: int(os.getenv('AGENT_TIMEOUT', '30')))
    enable_debug: bool = field(default_factory=lambda: os.getenv('ENABLE_DEBUG', 'False').lower() in ['true', '1', 'yes', 'on'])
    max_concurrent_agents: int = field(default_factory=lambda: int(os.getenv('MAX_CONCURRENT_AGENTS', '5')))
    
    # ============================================================================
    # PERFORMANCE SETTINGS
    # ============================================================================
    cache_size: int = field(default_factory=lambda: int(os.getenv('CACHE_SIZE', '1000')))
    cache_ttl: int = field(default_factory=lambda: int(os.getenv('CACHE_TTL', '3600')))  # 1 hour
    connection_pool_size: int = field(default_factory=lambda: int(os.getenv('CONNECTION_POOL_SIZE', '10')))
    
    # ============================================================================
    # SECURITY SETTINGS
    # ============================================================================
    allowed_users: List[str] = field(default_factory=lambda: os.getenv('ALLOWED_USERS', '').split(',') if os.getenv('ALLOWED_USERS') else [])
    rate_limit_per_user: int = field(default_factory=lambda: int(os.getenv('RATE_LIMIT_PER_USER', '100')))  # per hour
    enable_user_whitelist: bool = field(default_factory=lambda: os.getenv('ENABLE_USER_WHITELIST', 'False').lower() in ['true', '1', 'yes', 'on'])
    
    # ============================================================================
    # FEATURE FLAGS
    # ============================================================================
    enable_analytics: bool = field(default_factory=lambda: os.getenv('ENABLE_ANALYTICS', 'False').lower() in ['true', '1', 'yes', 'on'])
    enable_backup: bool = field(default_factory=lambda: os.getenv('ENABLE_BACKUP', 'True').lower() in ['true', '1', 'yes', 'on'])
    enable_health_checks: bool = field(default_factory=lambda: os.getenv('ENABLE_HEALTH_CHECKS', 'True').lower() in ['true', '1', 'yes', 'on'])
    
    def __post_init__(self):
        """Post-initialization setup and validation"""
        self._setup_logging()
        self._validate_configuration()
        self._create_directories()
        logger.info("🔧 Configuration initialized successfully")
    
    def _setup_logging(self) -> None:
        """Setup basic logging for configuration"""
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(getattr(logging, self.log_level.upper(), logging.INFO))
    
    def validate(self) -> None:
        """Public method to validate configuration (backward compatibility)"""
        self._validate_configuration()
    
    def _validate_configuration(self) -> None:
        """Validate required configuration and constraints"""
        errors = []
        warnings = []
        
        # Required fields validation
        required_fields = [
            ('telegram_token', self.telegram_token, 'TELEGRAM_BOT_TOKEN'),
            ('gemini_api_key', self.gemini_api_key, 'GEMINI_API_KEY'),
            ('sheets_id', self.sheets_id, 'GOOGLE_SHEETS_ID')
        ]
        
        for field_name, value, env_name in required_fields:
            if not value or value.strip() == '':
                errors.append(f"Missing required field: {field_name} (env: {env_name})")
        
        # File path validation
        if self.sheets_credentials_path:
            creds_path = Path(self.sheets_credentials_path)
            if not creds_path.exists():
                errors.append(f"Google Sheets credentials file not found: {self.sheets_credentials_path}")
            elif not creds_path.is_file():
                errors.append(f"Google Sheets credentials path is not a file: {self.sheets_credentials_path}")
        
        # Numeric constraints validation
        numeric_constraints = [
            ('gemini_temperature', self.gemini_temperature, 0.0, 2.0),
            ('gemini_max_tokens', self.gemini_max_tokens, 1, 32768),
            ('max_image_size', self.max_image_size, 1024, 10485760),  # 1KB to 10MB
            ('max_retries', self.max_retries, 1, 10),
            ('agent_timeout', self.agent_timeout, 5, 300),  # 5 seconds to 5 minutes
            ('cache_size', self.cache_size, 10, 10000),
            ('cache_ttl', self.cache_ttl, 60, 86400),  # 1 minute to 1 day
            ('connection_pool_size', self.connection_pool_size, 1, 50),
            ('rate_limit_per_user', self.rate_limit_per_user, 1, 1000),
            ('sheets_batch_size', self.sheets_batch_size, 1, 1000),
            ('max_concurrent_agents', self.max_concurrent_agents, 1, 20),
        ]
        
        for field_name, value, min_val, max_val in numeric_constraints:
            if not (min_val <= value <= max_val):
                warnings.append(f"{field_name} value {value} is outside recommended range [{min_val}, {max_val}]")
        
        # Log level validation
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level.upper() not in valid_log_levels:
            warnings.append(f"Invalid log level: {self.log_level}. Using INFO instead.")
            self.log_level = 'INFO'
        
        # Model validation
        valid_models = [
            'gemini-2.0-flash-exp',
            'gemini-2.5-flash',
            'gemini-1.5-pro',
            'gemini-1.5-flash'
        ]
        if self.gemini_model not in valid_models:
            warnings.append(f"Unknown Gemini model: {self.gemini_model}. Supported: {', '.join(valid_models)}")
        
        # Log warnings
        for warning in warnings:
            logger.warning(f"⚠️  Configuration warning: {warning}")
        
        # Raise errors if any
        if errors:
            error_message = "❌ Configuration validation failed:\n" + "\n".join(f"  • {error}" for error in errors)
            logger.error(error_message)
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        logger.info("✅ Configuration validation passed")
    
    def _create_directories(self) -> None:
        """Create necessary directories if they don't exist"""
        directories_to_create = [
            'logs',
            'temp',
            'backups',
            Path(self.sheets_credentials_path).parent if self.sheets_credentials_path else None
        ]
        
        for directory in directories_to_create:
            if directory:
                dir_path = Path(directory)
                if not dir_path.exists():
                    try:
                        dir_path.mkdir(parents=True, exist_ok=True)
                        logger.debug(f"📁 Created directory: {dir_path}")
                    except Exception as e:
                        logger.warning(f"⚠️  Failed to create directory {dir_path}: {e}")
    
    def get_database_url(self) -> Optional[str]:
        """Get database URL if configured (for future use)"""
        return os.getenv('DATABASE_URL')
    
    def get_redis_url(self) -> Optional[str]:
        """Get Redis URL if configured (for future caching)"""
        return os.getenv('REDIS_URL')
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return os.getenv('ENVIRONMENT', 'development').lower() == 'production'
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return os.getenv('ENVIRONMENT', 'development').lower() == 'development'
    
    def get_environment(self) -> str:
        """Get current environment"""
        return os.getenv('ENVIRONMENT', 'development')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding sensitive data)"""
        config_dict = {}
        sensitive_fields = {'telegram_token', 'gemini_api_key', 'sheets_credentials_path'}
        
        for field_name in self.__dataclass_fields__:
            value = getattr(self, field_name)
            if field_name in sensitive_fields:
                config_dict[field_name] = "***HIDDEN***" if value else "NOT_SET"
            else:
                config_dict[field_name] = value
        
        return config_dict
    
    def get_summary(self) -> str:
        """Get a formatted summary of the configuration"""
        summary = [
            "🔧 System Configuration Summary:",
            f"  • Environment: {self.get_environment()}",
            f"  • Log Level: {self.log_level}",
            f"  • Debug Mode: {'Enabled' if self.enable_debug else 'Disabled'}",
            f"  • Gemini Model: {self.gemini_model}",
            f"  • Max Retries: {self.max_retries}",
            f"  • Agent Timeout: {self.agent_timeout}s",
            f"  • Cache Size: {self.cache_size}",
            f"  • Health Checks: {'Enabled' if self.enable_health_checks else 'Disabled'}",
            f"  • Analytics: {'Enabled' if self.enable_analytics else 'Disabled'}",
            f"  • User Whitelist: {'Enabled' if self.enable_user_whitelist else 'Disabled'}",
        ]
        return "\n".join(summary)
    
    def reload_from_env(self) -> None:
        """Reload configuration from environment variables"""
        logger.info("🔄 Reloading configuration from environment...")
        load_dotenv(override=True)
        
        # Re-initialize the instance
        self.__init__()
        logger.info("✅ Configuration reloaded successfully")

# Global config instance
config = Config()

# Utility functions for common config operations
def get_config() -> Config:
    """Get the global configuration instance"""
    return config

def is_debug_enabled() -> bool:
    """Check if debug mode is enabled"""
    return config.enable_debug

def get_log_level() -> str:
    """Get the current log level"""
    return config.log_level

def validate_config() -> None:
    """Validate the current configuration"""
    config.validate()

# Export commonly used config values for convenience
GEMINI_MODEL = config.gemini_model
LOG_LEVEL = config.log_level
DEBUG_MODE = config.enable_debug
ENVIRONMENT = config.get_environment()