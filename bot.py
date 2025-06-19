"""
Enhanced Telegram Bot Handler for the Agentic AI Grocery Bot system.
"""
import base64
import logging
import asyncio

from io import BytesIO
from config import config
from telegram import Update
from src.agents import AgenticAgentManager
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logger = logging.getLogger(__name__)

class AgenticTelegramBotHandler:
    """Enhanced Telegram bot handler with agentic capabilities"""
    
    def __init__(self):
        self.agent_manager = AgenticAgentManager()
        self.app = Application.builder().token(config.telegram_token).build()
        self._setup_handlers()
        logger.info("🚀 Agentic Telegram Bot Handler initialized")
    
    def _setup_handlers(self):
        """Setup telegram bot message handlers"""
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("test", self.test_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(CommandHandler("analytics", self.analytics_command))
        self.app.add_handler(CommandHandler("agents", self.agents_command))
        self.app.add_handler(CommandHandler("memory", self.memory_command))
        self.app.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        logger.info("✅ Agentic bot handlers configured")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command with agentic features"""
        welcome = """
🤖 **Agentic AI-Powered Grocery Tracking System** 🤖

Welcome to your intelligent expense tracking assistant with advanced AI capabilities!

**🧠 Agentic AI Features:**
• Dynamic Planning & Reasoning
• Multi-Agent Collaboration  
• Intelligent Tool Selection
• Learning from Experience
• Adaptive Processing Strategies

**📸 Advanced Receipt Processing:**
• Computer vision with quality analysis
• Multi-pass processing for complex receipts
• Error recovery and adaptation
• Store-specific optimization

**💬 Intelligent Text Processing:**
• Natural language understanding
• Context-aware interpretation
• Ambiguity resolution
• Multi-language support

**🤝 Multi-Agent Coordination:**
• Agents collaborate when beneficial
• Shared context and knowledge
• Dynamic routing based on complexity
• Performance-based optimization

**🧠 Learning & Memory:**
• Agents learn from past experiences
• Pattern recognition for better results
• Performance tracking and optimization
• Continuous improvement

**Enhanced Commands:**
/start - This welcome message
/help - Detailed help & examples
/test - Test agentic system functionality
/status - Check system health & agent status
/analytics - View performance analytics
/agents - See agent capabilities & memory
/memory - View learning and collaboration history

Send me a receipt photo or expense text to experience agentic AI processing!
        """
        await update.message.reply_text(welcome, parse_mode='Markdown') # type: ignore
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command with agentic capabilities"""
        help_text = """
🆘 **Agentic AI Help Guide:**

**🧠 How Agentic AI Works:**
The system uses intelligent agents that can:
• Analyze input and create custom plans
• Choose the best tools dynamically
• Adapt when things don't go as expected
• Learn from each interaction
• Collaborate with other agents when needed

**📸 Agentic Receipt Processing:**
• Analyzes image quality first
• Creates processing strategy based on complexity
• Uses multiple validation steps
• Adapts approach if initial attempt fails
• Learns optimal strategies for different receipt types

**💬 Intelligent Text Processing:**
• Understands context and intent
• Resolves ambiguities through reasoning
• Infers missing information
• Validates results for logical consistency
• Learns language patterns and preferences

**🔧 Dynamic Tool Selection:**
Agents don't follow fixed workflows - they:
• Analyze the specific situation
• Choose tools based on context
• Switch strategies if needed
• Learn which tools work best when

**🤝 Multi-Agent Collaboration:**
For complex requests, multiple agents work together:
• Each contributes their expertise
• Results are synthesized intelligently
• Collaboration patterns are learned over time

**📝 Text Input Examples (Agentic Processing):**
• "Milk ₹60, Bread ₹40, Eggs ₹80" → Direct extraction
• "Bought some groceries for around ₹500" → Inference reasoning
• "Spent money on vegetables" → Clarification strategy
• "टमाटर ₹30, प्याज़ ₹25" → Multi-language processing

**🧠 Learning Features:**
• Remembers successful processing strategies
• Adapts to your input patterns
• Improves accuracy over time
• Learns optimal agent collaboration

**⚡ Advanced Commands:**
/analytics - View system performance and learning
/agents - See individual agent capabilities and memories
/memory - View collaboration history and patterns

**💡 Pro Tips:**
• The system gets smarter with each use
• Complex receipts are handled with adaptive strategies
• Ambiguous text triggers intelligent clarification
• Multiple processing attempts for better accuracy
        """
        await update.message.reply_text(help_text, parse_mode='Markdown') # type: ignore
    
    async def test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test agentic system functionality"""
        await update.message.reply_text("🧪 Running agentic system tests...") # type: ignore
        
        try:
            # Get comprehensive system status
            status = await self.agent_manager.get_system_status()
            
            test_result = "🧪 **Agentic System Test Results:**\n\n"
            test_result += f"**System Type:** {status.get('system_type', 'Unknown')}\n"
            test_result += f"**Agents Available:** {status.get('agents', 0)}\n"
            test_result += f"**Gemini Service:** {status.get('gemini_service', '❌ Unknown')}\n"
            test_result += f"**Sheets Service:** {status.get('sheets_service', '❌ Unknown')}\n\n"
            
            # Agentic features status
            agentic_features = status.get('agentic_features', {})
            test_result += "**🧠 Agentic Features:**\n"
            for feature, status_val in agentic_features.items():
                test_result += f"• {feature.replace('_', ' ').title()}: {status_val}\n"
            
            # Agent memory status
            agent_memories = status.get('agent_memories', {})
            if agent_memories:
                test_result += "\n**🧠 Agent Learning Status:**\n"
                for agent_name, memory in agent_memories.items():
                    short_name = agent_name.split()[-2] if len(agent_name.split()) > 2 else agent_name
                    test_result += f"• {short_name}: {memory['experiences']} experiences, {memory['success_patterns']} patterns\n"
            
            # Collaboration stats
            collab_stats = status.get('collaboration_stats', {})
            if collab_stats:
                test_result += f"\n**🤝 Collaboration:** {collab_stats.get('total_collaborations', 0)} total, {collab_stats.get('recent_collaborations_today', 0)} today\n"
            
            if 'error' in status:
                test_result += f"\n❌ **System Error:** {status['error']}"
            else:
                test_result += "\n✅ **All agentic systems operational!**"
            
            await update.message.reply_text(test_result, parse_mode='Markdown') # type: ignore
            
        except Exception as e:
            await update.message.reply_text(f"❌ **Agentic Test Failed:** {str(e)}") # type: ignore
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show detailed agentic system status"""
        try:
            status = await self.agent_manager.get_system_status()
            agents_info = self.agent_manager.list_agents()
            
            status_text = "📊 **Agentic System Status Dashboard:**\n\n"
            status_text += f"**System Type:** {status.get('system_type', 'Unknown')}\n\n"
            
            status_text += f"**Service Health:**\n"
            status_text += f"• Gemini AI: {status.get('gemini_service', '❌ Unknown')}\n"
            status_text += f"• Google Sheets: {status.get('sheets_service', '❌ Unknown')}\n"
            status_text += f"• Configuration: {status.get('config_valid', '❌ Invalid')}\n\n"
            
            status_text += f"**🧠 Agentic Capabilities:**\n"
            agentic_features = status.get('agentic_features', {})
            for feature, feature_status in agentic_features.items():
                feature_name = feature.replace('_', ' ').title()
                status_text += f"• {feature_name}: {feature_status}\n"
            
            status_text += f"\n**🤖 Available Agents:**\n"
            for name, description in agents_info.items():
                short_name = name.split()[-2] if len(name.split()) > 2 else name
                capabilities = description.split("Capabilities: ")[-1] if "Capabilities: " in description else "Unknown"
                status_text += f"• {short_name}: {capabilities[:50]}...\n"
            
            status_text += f"\n**⚙️ Configuration:**\n"
            status_text += f"• Model: {config.gemini_model}\n"
            status_text += f"• Debug Mode: {'On' if config.enable_debug else 'Off'}\n"
            status_text += f"• Learning: {'Enabled' if config.enable_analytics else 'Disabled'}\n"
            
            await update.message.reply_text(status_text, parse_mode='Markdown') # type: ignore
            
        except Exception as e:
            await update.message.reply_text(f"❌ **Status Check Failed:** {str(e)}") # type: ignore
    
    async def analytics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show performance analytics and learning insights"""
        try:
            await update.message.reply_text("📊 Analyzing system performance and learning...") # type: ignore
            
            # Get collaboration effectiveness
            collab_analysis = await self.agent_manager.analyze_agent_collaboration_effectiveness()
            
            # Get global context summary
            context_summary = self.agent_manager.get_global_context_summary()
            
            analytics_text = "📊 **Performance Analytics & Learning Insights:**\n\n"
            
            # Collaboration analysis
            if collab_analysis.get("total_collaborations", 0) > 0:
                analytics_text += "**🤝 Collaboration Analysis:**\n"
                analytics_text += f"• Total Collaborations: {collab_analysis['total_collaborations']}\n"
                analytics_text += f"• Success Rate: {collab_analysis['overall_success_rate']:.2%}\n"
                
                most_effective = collab_analysis.get('most_effective_pair')
                if most_effective:
                    analytics_text += f"• Most Effective Pair: {most_effective[0]} ({most_effective[1]['success_rate']:.2%})\n"
            else:
                analytics_text += "**🤝 Collaboration:** No collaborations yet\n"
            
            # Learning context
            analytics_text += f"\n**🧠 Learning Context:**\n"
            analytics_text += f"• Recent Requests: {context_summary['recent_requests_count']}\n"
            analytics_text += f"• Routing Decisions: {context_summary['routing_history_count']}\n"
            analytics_text += f"• Last Update: {context_summary.get('context_last_updated', 'Never')[:19] if context_summary.get('context_last_updated') != 'Never' else 'Never'}\n"
            
            # Performance insights
            performance_insights = context_summary.get('performance_insights', {})
            if performance_insights:
                analytics_text += f"\n**⚡ Agent Performance:**\n"
                for agent, metrics in performance_insights.items():
                    short_name = agent.split()[-2] if len(agent.split()) > 2 else agent
                    analytics_text += f"• {short_name}: {metrics['success_rate']:.2%} success ({metrics['total_requests']} requests)\n"
            
            analytics_text += f"\n💡 *System continuously learns and improves from each interaction*"
            
            await update.message.reply_text(analytics_text, parse_mode='Markdown') # type: ignore
            
        except Exception as e:
            await update.message.reply_text(f"❌ **Analytics Failed:** {str(e)}") # type: ignore
    
    async def agents_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show detailed agent information and capabilities"""
        try:
            agents_text = "🤖 **Agent Capabilities & Memory Status:**\n\n"
            
            for agent_name, agent in self.agent_manager.agents.items():
                short_name = agent_name.split()[-2] if len(agent_name.split()) > 2 else agent_name
                
                agents_text += f"**{short_name}:**\n"
                agents_text += f"• Description: {agent.description[:60]}...\n"
                agents_text += f"• Capabilities: {len(agent.capabilities)} total\n"
                
                # Memory summary
                memory_summary = agent.get_memory_summary()
                agents_text += f"• Experiences: {memory_summary['total_experiences']}\n"
                agents_text += f"• Success Patterns: {len(memory_summary['successful_patterns'])}\n"
                
                # Current plan status
                plan_status = agent.get_current_plan_status()
                if plan_status:
                    agents_text += f"• Current Plan: {plan_status['progress']:.0%} complete\n"
                else:
                    agents_text += f"• Current Plan: None active\n"
                
                agents_text += "\n"
            
            agents_text += "💡 *Each agent learns and improves independently while collaborating when beneficial*"
            
            await update.message.reply_text(agents_text, parse_mode='Markdown') # type: ignore
            
        except Exception as e:
            await update.message.reply_text(f"❌ **Agent Info Failed:** {str(e)}") # type: ignore
    
    async def memory_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show learning and memory information"""
        try:
            memory_text = "🧠 **System Learning & Memory:**\n\n"
            
            # Get global context summary
            context_summary = self.agent_manager.get_global_context_summary()
            
            memory_text += "**📚 Global Learning:**\n"
            memory_text += f"• Recent Requests Tracked: {context_summary['recent_requests_count']}\n"
            memory_text += f"• Routing Decisions Made: {context_summary['routing_history_count']}\n"
            memory_text += f"• Collaboration Sessions: {context_summary['collaboration_history_count']}\n"
            
            # Individual agent memories
            memory_text += "\n**🤖 Agent Memories:**\n"
            for agent_name, agent in self.agent_manager.agents.items():
                short_name = agent_name.split()[-2] if len(agent_name.split()) > 2 else agent_name
                memory_summary = agent.get_memory_summary()
                
                if memory_summary['total_experiences'] > 0:
                    memory_text += f"• {short_name}: {memory_summary['total_experiences']} experiences"
                    
                    # Show top success pattern
                    if memory_summary['successful_patterns']:
                        top_pattern = max(memory_summary['successful_patterns'].items(), key=lambda x: x[1])
                        memory_text += f", best pattern: {top_pattern[0]} ({top_pattern[1]} times)\n"
                    else:
                        memory_text += "\n"
                else:
                    memory_text += f"• {short_name}: No experiences yet\n"
            
            # Recent learning insights
            performance_insights = context_summary.get('performance_insights', {})
            if performance_insights:
                memory_text += "\n**📈 Recent Performance Insights:**\n"
                for agent, metrics in list(performance_insights.items())[:3]:  # Top 3
                    short_name = agent.split()[-2] if len(agent.split()) > 2 else agent
                    memory_text += f"• {short_name}: {metrics['success_rate']:.1%} success rate\n"
            
            memory_text += "\n💡 *System memory helps optimize future processing decisions*"
            
            await update.message.reply_text(memory_text, parse_mode='Markdown') # type: ignore
            
        except Exception as e:
            await update.message.reply_text(f"❌ **Memory Info Failed:** {str(e)}") # type: ignore
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle receipt photos with agentic processing"""
        logger.info("📸 Photo received - routing to Agentic Processing System")
        
        try:
            await update.message.reply_text( # type: ignore
                "🤖 **Agentic AI Receipt Processing Activated**\n"
                "🧠 Analyzing image and creating intelligent plan...\n"
                "⏳ Please wait while AI agents process your receipt..."
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
            
            # Process with Agentic AI System
            result = await self.agent_manager.intelligent_route_request(
                image_data=image_data,
                message_date=message_date
            )
            
            # Send result with agentic details
            if result.success:
                response = f"🤖 **Agentic AI Processing Complete:**\n\n{result.message}"
                
                # Add processing insights if available
                if result.data and isinstance(result.data, dict):
                    if "processing_strategy" in result.data:
                        response += f"\n\n🎯 **Processing Strategy:** {result.data['processing_strategy']}"
                    
                    if "plan_summary" in result.data:
                        plan_summary = result.data["plan_summary"]
                        response += f"\n📋 **Plan Execution:** {plan_summary['successful_tasks']}/{plan_summary['total_tasks']} tasks successful"
                    
                    if "collaboration_summary" in result.data:
                        collab_summary = result.data["collaboration_summary"]
                        response += f"\n🤝 **Collaboration:** {collab_summary['successful_agents']}/{collab_summary['total_agents']} agents contributed"
            else:
                response = f"❌ **Agentic Processing Error:**\n{result.message}"
                if result.error:
                    response += f"\n\n**Technical Details:**\n{result.error}"
            
            await update.message.reply_text(response) # type: ignore
            
        except Exception as e:
            logger.error(f"Agentic photo handler error: {e}")
            await update.message.reply_text(f"❌ **System Error:** {str(e)}") # type: ignore
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages with agentic processing"""
        text = update.message.text # type: ignore
        logger.info(f"💬 Text received - routing to Agentic Processing System: {text[:50]}...") # type: ignore
        
        # Enhanced expense keyword detection
        expense_keywords = ['₹', 'rupees', 'rs', 'cost', 'price', 'bought', 'purchased', 'expense', 'spent', 'paid', 'bill', 'shopping']
        
        if any(keyword in text.lower() for keyword in expense_keywords): # type: ignore
            try:
                await update.message.reply_text( # type: ignore
                    "🤖 **Agentic AI Text Processing Activated**\n"
                    "🧠 Analyzing language and creating intelligent plan...\n"
                    "⏳ Please wait while AI agents understand your text..."
                )
                
                message_date = update.message.date.strftime('%Y-%m-%d') # type: ignore
                
                # Process with Agentic AI System
                result = await self.agent_manager.intelligent_route_request(
                    text=text, # type: ignore
                    message_date=message_date
                )
                
                # Send result with agentic insights
                if result.success:
                    response = f"🤖 **Agentic AI Processing Complete:**\n\n{result.message}"
                    
                    # Add processing insights
                    if result.data and isinstance(result.data, dict):
                        if "processing_strategy" in result.data:
                            response += f"\n\n🎯 **Processing Strategy:** {result.data['processing_strategy']}"
                        
                        if "language_analysis" in result.data:
                            lang_analysis = result.data["language_analysis"]
                            response += f"\n🗣️ **Language:** {lang_analysis.get('language', 'unknown')} (confidence: {lang_analysis.get('intent_confidence', 0):.2f})"
                        
                        if "plan_summary" in result.data:
                            plan_summary = result.data["plan_summary"]
                            response += f"\n📋 **Plan Execution:** {plan_summary['successful_tasks']}/{plan_summary['total_tasks']} tasks successful"
                        
                        if "collaboration_summary" in result.data:
                            collab_summary = result.data["collaboration_summary"]
                            response += f"\n🤝 **Collaboration:** {collab_summary['successful_agents']}/{collab_summary['total_agents']} agents contributed"
                else:
                    response = f"❌ **Agentic Processing Error:**\n{result.message}"
                    if result.error:
                        response += f"\n\n**Technical Details:**\n{result.error}"
                
                await update.message.reply_text(response) # type: ignore
                
            except Exception as e:
                logger.error(f"Agentic text handler error: {e}") # type: ignore
                await update.message.reply_text(f"❌ **System Error:** {str(e)}") # type: ignore
        else:
            # Enhanced non-expense response with agentic capabilities
            await update.message.reply_text( # type: ignore
                "🤖 **Agentic AI Analysis:** No expense keywords detected.\n\n"
                "🧠 **Smart Tip:** The AI can understand various expense formats:\n\n"
                "📝 **Try these examples:**\n"
                "• 'Milk ₹60, Bread ₹40'\n"
                "• 'Bought groceries for ₹500'\n"
                "• 'Spent ₹150 on vegetables'\n"
                "• 'Shopping bill was ₹300'\n"
                "• 'Paid ₹80 for fruits'\n\n"
                "📸 **Or send a receipt photo for automatic agentic processing!**\n\n"
                "💡 The system learns your patterns and gets smarter with each use."
            )
    
    def run(self):
        """Start the agentic telegram bot"""
        logger.info("🚀 Starting Agentic AI-Powered Grocery Bot...")
        logger.info("🧠 Active Features: Intelligent Routing, Multi-Agent Collaboration, Dynamic Planning")
        logger.info("🤖 Available Agents: Receipt Processor + Text Processor with Learning Capabilities")
        logger.info("📊 Data Format: Date | Original Name | Clean Name | Pieces | Unit Size | Total Qty | Price | Value")
        logger.info("🔄 Ready for agentic AI expense processing!")
        
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
            logger.info("🛑 Agentic bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Agentic bot error: {e}")
        finally:
            # Clean up
            try:
                if not loop.is_closed(): # type: ignore
                    loop.close() # type: ignore
            except:
                pass

# For backward compatibility
TelegramBotHandler = AgenticTelegramBotHandler