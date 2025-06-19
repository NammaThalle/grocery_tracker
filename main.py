"""
Main entry point for the AI-Powered Grocery Tracking System.
"""
import logging
import asyncio

from pathlib import Path
from config import config
from bot import TelegramBotHandler
from src.services import GoogleSheetsService

def setup_logging():
    """Configure application logging"""
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format=log_format,
        handlers=[
            logging.FileHandler(logs_dir / "grocery_bot.log"),
            logging.StreamHandler()
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("telegram").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info("📝 Logging system initialized")
    return logger

async def initialize_services():                                                                                                                                 
    """Initialize all required services"""
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize Google Sheets and create headers if needed
        logger.info("📊 Initializing Google Sheets service...")
        sheets_service = GoogleSheetsService()
        await sheets_service.create_headers_if_needed()
        
        logger.info("✅ All services initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Service initialization failed: {e}")
        return False

def print_startup_banner():
    """Print application startup banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║           🤖 AI-POWERED GROCERY TRACKING SYSTEM 🤖           ║
    ║                                                              ║
    ║  🔬 Powered by: LangChain Agents + Gemini 2.0 + Python     ║
    ║  🏗️  Architecture: Modular, Scalable, Production-Ready      ║
    ║  🎯 Capabilities: Smart Receipt OCR + NLP Text Processing   ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_system_info():
    """Print system configuration information"""
    logger = logging.getLogger(__name__)
    
    logger.info("🔧 System Configuration:")
    logger.info(f"   • Model: {config.gemini_model}")
    logger.info(f"   • Max Retries: {config.max_retries}")
    logger.info(f"   • Log Level: {config.log_level}")
    logger.info(f"   • Debug Mode: {'Enabled' if config.enable_debug else 'Disabled'}")
    logger.info(f"   • Agent Timeout: {config.agent_timeout}s")
    
    logger.info("📊 Data Pipeline:")
    logger.info("   • Receipt Agent: Image → Gemini Vision → JSON → Sheets")
    logger.info("   • Text Agent: Text → Gemini NLP → JSON → Sheets")
    logger.info("   • Format: Date|Original|Clean|Pieces|Unit|Total|Price|Value")

def main():
    """Main application entry point - synchronous version"""
    # Setup logging
    logger = setup_logging()
    
    try:
        # Print startup information
        print_startup_banner()
        print_system_info()
        
        # Validate configuration
        logger.info("🔍 Validating configuration...")
        config.validate()
        logger.info("✅ Configuration validation successful")
        
        # Initialize services in a separate event loop
        logger.info("🚀 Initializing system services...")
        
        # Create new event loop for initialization
        init_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(init_loop)
        
        try:
            # Initialize services
            success = init_loop.run_until_complete(initialize_services())
            if not success:
                logger.error("❌ Failed to initialize services")
                return
        finally:
            # Close initialization loop
            init_loop.close()
            # Clear the event loop so bot can create its own
            asyncio.set_event_loop(None)
        
        # Start the bot
        logger.info("🤖 Starting Telegram Bot with Agent System...")
        bot_handler = TelegramBotHandler()
        
        logger.info("🎯 System ready! Bot is now active and waiting for messages...")
        logger.info("📱 Send receipt photos or expense text to your Telegram bot")
        
        # Run the bot (blocking call) - this handles its own event loop
        bot_handler.run()
        
    except KeyboardInterrupt:
        logger.info("🛑 Application stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Application failed to start: {e}")
        if config.enable_debug:
            import traceback
            logger.error("🐛 Debug traceback:")
            logger.error(traceback.format_exc())
    finally:
        logger.info("👋 Grocery Tracking System shutdown complete")

if __name__ == "__main__":
    """Entry point when running the script directly"""
    try:
        main()  # Call synchronous main function
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")