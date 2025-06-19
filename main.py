"""
Main entry point for the Agentic AI-Powered Grocery Tracking System.
"""
import logging
import asyncio

from pathlib import Path
from config import config
from bot import AgenticTelegramBotHandler
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
            logging.FileHandler(logs_dir / "agentic_grocery_bot.log"),
            logging.StreamHandler()
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("telegram").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info("📝 Agentic logging system initialized")
    return logger

async def initialize_services():
    """Initialize all required services"""
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize Google Sheets and create headers if needed
        logger.info("📊 Initializing Google Sheets service...")
        sheets_service = GoogleSheetsService()
        await sheets_service.create_headers_if_needed()
        
        logger.info("✅ All agentic services initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Service initialization failed: {e}")
        return False

def print_startup_banner():
    """Print application startup banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║         🧠 AGENTIC AI-POWERED GROCERY TRACKING SYSTEM 🧠     ║
    ║                                                              ║
    ║  🤖 Powered by: Multi-Agent AI + Gemini 2.0 + Python       ║
    ║  🏗️  Architecture: Agentic, Self-Improving, Collaborative   ║
    ║  🎯 Capabilities: Dynamic Planning + Reasoning + Learning   ║
    ║                                                              ║
    ║  🧠 AGENTIC FEATURES:                                        ║
    ║     • Intelligent Planning & Reasoning                       ║
    ║     • Dynamic Tool Selection                                 ║
    ║     • Multi-Agent Collaboration                              ║
    ║     • Learning from Experience                               ║
    ║     • Adaptive Error Recovery                                ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_system_info():
    """Print system configuration information"""
    logger = logging.getLogger(__name__)
    
    logger.info("🔧 Agentic System Configuration:")
    logger.info(f"   • AI Model: {config.gemini_model}")
    logger.info(f"   • Max Retries: {config.max_retries}")
    logger.info(f"   • Log Level: {config.log_level}")
    logger.info(f"   • Debug Mode: {'Enabled' if config.enable_debug else 'Disabled'}")
    logger.info(f"   • Agent Timeout: {config.agent_timeout}s")
    logger.info(f"   • Learning: {'Enabled' if config.enable_analytics else 'Disabled'}")
    
    logger.info("🧠 Agentic AI Pipeline:")
    logger.info("   • Input Analysis → Dynamic Planning → Tool Selection")
    logger.info("   • Multi-Agent Coordination → Adaptive Execution")
    logger.info("   • Result Synthesis → Learning & Memory Update")
    logger.info("   • Format: Date|Original|Clean|Pieces|Unit|Total|Price|Value")
    
    logger.info("🤖 Agent Capabilities:")
    logger.info("   • Receipt Agent: Vision Analysis + Quality Assessment + Adaptation")
    logger.info("   • Text Agent: NLP + Context Understanding + Ambiguity Resolution")
    logger.info("   • Tool Registry: Dynamic Selection + Performance Learning")
    logger.info("   • Agent Manager: Intelligent Routing + Collaboration + Optimization")

def main():
    """Main application entry point - synchronous version"""
    # Setup logging
    logger = setup_logging()
    
    try:
        # Print startup information
        print_startup_banner()
        print_system_info()
        
        # Validate configuration
        logger.info("🔍 Validating agentic system configuration...")
        config.validate()
        logger.info("✅ Configuration validation successful")
        
        # Initialize services in a separate event loop
        logger.info("🚀 Initializing agentic system services...")
        
        # Create new event loop for initialization
        init_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(init_loop)
        
        try:
            # Initialize services
            success = init_loop.run_until_complete(initialize_services())
            if not success:
                logger.error("❌ Failed to initialize agentic services")
                return
        finally:
            # Close initialization loop
            init_loop.close()
            # Clear the event loop so bot can create its own
            asyncio.set_event_loop(None)
        
        # Start the agentic bot
        logger.info("🤖 Starting Agentic Telegram Bot with Multi-Agent System...")
        bot_handler = AgenticTelegramBotHandler()
        
        logger.info("🎯 Agentic AI System ready! Bot is now active and learning...")
        logger.info("📱 Send receipt photos or expense text to experience agentic AI processing")
        logger.info("🧠 System will learn and improve with each interaction")
        
        # Run the bot (blocking call) - this handles its own event loop
        bot_handler.run()
        
    except KeyboardInterrupt:
        logger.info("🛑 Agentic application stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Agentic application failed to start: {e}")
        if config.enable_debug:
            import traceback
            logger.error("🐛 Debug traceback:")
            logger.error(traceback.format_exc())
    finally:
        logger.info("👋 Agentic Grocery Tracking System shutdown complete")

if __name__ == "__main__":
    """Entry point when running the script directly"""
    try:
        main()  # Call synchronous main function
    except KeyboardInterrupt:
        print("\n👋 Goodbye from Agentic AI!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")