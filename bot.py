"""
Telegram Bot Handler for the Grocery Bot system.
"""
import base64
import logging
import asyncio

from io import BytesIO
from config import config
from telegram import Update
from src.agents import AgentManager
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logger = logging.getLogger(__name__)

class TelegramBotHandler:
    """Handles all Telegram bot interactions"""
    
    def __init__(self):
        self.agent_manager = AgentManager()
        self.app = Application.builder().token(config.telegram_token).build()
        self._setup_handlers()
        logger.info("🚀 Telegram Bot Handler initialized")
    
    def _setup_handlers(self):
        """Setup telegram bot message handlers"""
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("test", self.test_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        logger.info("✅ Bot handlers configured")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome = """
            🤖 **AI-Powered Grocery Tracking System** 🤖

            Welcome to your intelligent expense tracking assistant!

            **🔬 Powered by:**
            • LangChain Agent System
            • Gemini 2.0 AI Models  
            • Modular Architecture
            • Smart Data Processing

            **📸 Receipt Processing:**
            • Advanced computer vision
            • Intelligent item extraction
            • Automatic price detection
            • Store & date recognition

            **💬 Text Processing:**
            • Natural language understanding
            • Context-aware parsing
            • Smart categorization
            • Flexible input formats

            **🎯 Key Features:**
            • Multi-agent coordination
            • Robust error handling
            • Detailed logging
            • Production-ready design

            **Commands:**
            /start - This welcome message
            /help - Detailed help & examples
            /test - Test system functionality
            /status - Check system health

            Send me a receipt photo or expense text to get started!
        """
        await update.message.reply_text(welcome, parse_mode='Markdown') # type: ignore
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
            🆘 **Comprehensive Help Guide:**

            **📸 Receipt Processing Agent:**
            • Analyzes receipt images with Gemini 2.0 Vision
            • Extracts items, prices, store information
            • Handles complex receipt formats automatically
            • Recognizes various date formats
            • Processes package sizes intelligently

            **💬 Text Expense Agent:**
            • Understands natural language expense entries
            • Processes various text formats flexibly
            • Intelligent item categorization
            • Smart unit detection (kg/pcs/g/L)
            • Context-aware price parsing

            **📊 Data Processing:**
            • Automatic item name cleaning
            • Package size calculation
            • Unit conversion (g→kg when appropriate)
            • Price per unit calculation
            • Duplicate detection

            **🏗️ System Architecture:**
            • Modular agent-based design
            • Singleton services for efficiency
            • Robust error handling & recovery
            • Comprehensive logging
            • Production-ready scalability

            **📝 Text Input Examples:**
            • "Milk ₹60, Bread ₹40, Eggs ₹80"
            • "Bought vegetables: Tomatoes ₹30, Onions ₹25"
            • "Grocery shopping cost ₹500 - Apples 2kg, Rice 5kg"
            • "Spent ₹150 on fruits today"

            **🔧 System Commands:**
            /start - Welcome & overview
            /help - This detailed guide
            /test - Test agent functionality
            /status - System health check

            **💡 Pro Tips:**
            • Clear, well-lit receipt photos work best
            • Include ₹ symbol or price keywords in text
            • Multiple items can be processed at once
            • System learns from usage patterns
        """
        await update.message.reply_text(help_text, parse_mode='Markdown') # type: ignore
    
    async def test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test system functionality"""
        await update.message.reply_text("🧪 Running system tests...") # type: ignore
        
        try:
            # Get system status
            status = await self.agent_manager.get_system_status()
            
            test_result = "🧪 **System Test Results:**\n\n"
            test_result += f"**Agents Available:** {status.get('agents', 0)}\n"
            test_result += f"**Gemini Service:** {status.get('gemini_service', '❌ Unknown')}\n"
            test_result += f"**Sheets Service:** {status.get('sheets_service', '❌ Unknown')}\n"
            test_result += f"**Configuration:** {status.get('config_valid', '❌ Invalid')}\n\n"
            
            if 'available_agents' in status:
                test_result += "**Active Agents:**\n"
                for agent in status['available_agents']:
                    test_result += f"• {agent}\n"
            
            if 'error' in status:
                test_result += f"\n❌ **System Error:** {status['error']}"
            else:
                test_result += "\n✅ **All systems operational!**"
            
            await update.message.reply_text(test_result, parse_mode='Markdown') # type: ignore
            
        except Exception as e:
            await update.message.reply_text(f"❌ **Test Failed:** {str(e)}") # type: ignore
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show detailed system status"""
        try:
            status = await self.agent_manager.get_system_status()
            agents_info = self.agent_manager.list_agents()
            
            status_text = "📊 **System Status Dashboard:**\n\n"
            status_text += f"**Service Health:**\n"
            status_text += f"• Gemini AI: {status.get('gemini_service', '❌ Unknown')}\n"
            status_text += f"• Google Sheets: {status.get('sheets_service', '❌ Unknown')}\n"
            status_text += f"• Configuration: {status.get('config_valid', '❌ Invalid')}\n\n"
            
            status_text += f"**Agent System:**\n"
            status_text += f"• Total Agents: {len(agents_info)}\n"
            for name, description in agents_info.items():
                status_text += f"• {name}: Online ✅\n"
            
            status_text += f"\n**Configuration:**\n"
            status_text += f"• Model: {config.gemini_model}\n"
            status_text += f"• Max Retries: {config.max_retries}\n"
            status_text += f"• Debug Mode: {'On' if config.enable_debug else 'Off'}\n"
            
            await update.message.reply_text(status_text, parse_mode='Markdown') # type: ignore
            
        except Exception as e:
            await update.message.reply_text(f"❌ **Status Check Failed:** {str(e)}") # type: ignore
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle receipt photos with receipt processing agent"""
        logger.info("📸 Photo received - routing to Receipt Processing Agent")
        
        try:
            await update.message.reply_text( # type: ignore
                "🤖 **Receipt Processing Agent Activated**\n"
                "📸 Analyzing image with Gemini 2.0 Vision...\n"
                "⏳ Please wait while I extract the data..."
            )
            
            # Download and encode photo
            photo = update.message.photo[-1] # type: ignore
            file = await context.bot.get_file(photo.file_id)
            file_bytes = BytesIO()
            await file.download_to_memory(file_bytes)
            file_bytes.seek(0)
            
            # Convert to base64
            image_data = base64.b64encode(file_bytes.read()).decode('utf-8')
            message_date = update.message.date.strftime('%Y-%m-%d') # type: ignore
            
            # Process with Receipt Processing Agent
            result = await self.agent_manager.process_receipt_image(
                image_data=image_data,
                message_date=message_date
            )
            
            # Send result
            if result.success:
                response = f"🤖 **Receipt Processing Agent Results:**\n\n{result.message}"
            else:
                response = f"❌ **Agent Error:**\n{result.message}"
                if result.error:
                    response += f"\n\n**Technical Details:**\n{result.error}"
            
            await update.message.reply_text(response) # type: ignore
            
        except Exception as e:
            logger.error(f"Photo handler error: {e}")
            await update.message.reply_text(f"❌ **System Error:** {str(e)}") # type: ignore
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages with text expense agent"""
        text = update.message.text # type: ignore
        logger.info(f"💬 Text received - routing to Text Expense Agent: {text[:50]}...") # type: ignore
        
        # Check for expense keywords
        expense_keywords = ['₹', 'rupees', 'rs', 'cost', 'price', 'bought', 'purchased', 'expense', 'spent']
        
        if any(keyword in text.lower() for keyword in expense_keywords): # type: ignore
            try:
                await update.message.reply_text( # type: ignore
                    "🤖 **Text Expense Agent Activated**\n"
                    "🧠 Analyzing expense data with AI...\n"
                    "⏳ Processing natural language input..."
                )
                
                message_date = update.message.date.strftime('%Y-%m-%d') # type: ignore
                
                # Process with Text Expense Agent
                result = await self.agent_manager.process_text_expense(
                    text=text, # type: ignore
                    message_date=message_date
                )
                
                # Send result
                if result.success:
                    response = f"🤖 **Text Expense Agent Results:**\n\n{result.message}"
                else:
                    response = f"❌ **Agent Error:**\n{result.message}"
                    if result.error:
                        response += f"\n\n**Technical Details:**\n{result.error}"
                
                await update.message.reply_text(response) # type: ignore
                
            except Exception as e:
                logger.error(f"Text handler error: {e}") # type: ignore
                await update.message.reply_text(f"❌ **System Error:** {str(e)}") # type: ignore
        else:
            await update.message.reply_text( # type: ignore
                "🤖 **AI Analysis:** No expense keywords detected.\n\n"
                "💡 **Smart Tip:** Include ₹ symbol or expense keywords for processing.\n\n"
                "📝 **Example Formats:**\n"
                "• 'Milk ₹60, Bread ₹40'\n"
                "• 'Bought groceries for ₹500'\n"
                "• 'Spent ₹150 on vegetables'\n"
                "• 'Tomatoes cost ₹30, Onions ₹25'\n\n"
                "📸 **Or send a receipt photo for automatic processing!**"
            )
    
    def run(self):
        """Start the telegram bot"""
        logger.info("🚀 Starting AI-Powered Grocery Bot with Agent System...")
        logger.info("🤖 Active Agents: Receipt Processor + Text Processor")
        logger.info("📊 Data Format: Date | Original Name | Clean Name | Pieces | Unit Size | Total Qty | Price | Value")
        logger.info("🔄 Ready for intelligent expense processing!")
        
        # Create a new event loop for the bot
        try:
            # Get or create event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run the bot
            loop.run_until_complete(self.app.run_polling(drop_pending_updates=True)) # type: ignore
            
        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Bot error: {e}")
        finally:
            # Clean up
            try:
                if not loop.is_closed(): # type: ignore
                    loop.close() # type: ignore
            except:
                pass