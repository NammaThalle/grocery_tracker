# 🤖 AI-Powered Grocery Tracking System

## 📖 Overview

A sophisticated, modular AI-powered system for automated grocery expense tracking via Telegram. The system processes receipt images and natural language text to extract, categorize, and store expense data in Google Sheets using Google Gemini 2.0 AI.

### 🎯 Key Features

- **📸 Receipt OCR Processing** - Advanced computer vision with Gemini 2.0 Vision
- **💬 Natural Language Processing** - Smart text expense extraction
- **🤖 Multi-Agent Architecture** - Specialized agents for different tasks
- **🔧 Modular Tool System** - Reusable, extensible components
- **📊 Automated Data Storage** - Direct integration with Google Sheets
- **🏗️ Production-Ready Design** - Singleton patterns, error handling, logging
- **⚡ Async Processing** - Non-blocking operations for better performance

## 🏗️ Architecture

### **Four-Layer Modular Design:**

```
┌─────────────────────────────────────────────┐
│  🎯 Interface Layer (Telegram Bot)          │
├─────────────────────────────────────────────┤
│  🧠 Application Layer (Agent System)        │
├─────────────────────────────────────────────┤
│  🔧 Tools Layer (Processing Tools)          │
├─────────────────────────────────────────────┤
│  🏗️ Infrastructure (Services & Models)      │
└─────────────────────────────────────────────┘
```

### **Design Patterns Used:**
- **Singleton Pattern** - Services (Gemini, Sheets, Agent Manager)
- **Agent Pattern** - Specialized processing agents
- **Tool Pattern** - Modular, reusable tools
- **Factory Pattern** - Service creation and dependency injection
- **Strategy Pattern** - Different processing approaches

## 📁 Project Structure

```
grocery_bot_system/
├── main.py                     # Application entry point
├── bot.py                      # Telegram bot handler
├── config.py                   # Enhanced configuration management
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Docker deployment
├── .env.example               # Environment template
├── src/                       # Source code modules
│   ├── agents/                # Agent system
│   │   ├── __init__.py
│   │   ├── base.py           # Abstract base agent
│   │   ├── receipt_processing.py  # Receipt processing agent
│   │   ├── text_expense.py   # Text expense agent
│   │   └── manager.py        # Agent manager (singleton)
│   ├── tools/                 # Processing tools
│   │   ├── __init__.py
│   │   ├── base.py           # Abstract base tool
│   │   ├── process_receipt.py # Receipt image processing
│   │   ├── extract_text_expense.py # Text expense extraction
│   │   ├── save_to_sheets.py # Google Sheets integration
│   │   └── registry.py       # Tool discovery and execution
│   ├── services/              # External service integrations
│   │   ├── __init__.py
│   │   ├── base.py           # Service interfaces and protocols
│   │   ├── gemini.py         # Gemini AI service
│   │   ├── google_sheets.py  # Google Sheets service
│   │   ├── prompts.py        # AI prompt management
│   │   └── factory.py        # Service factory and DI
│   └── models/                # Data models and utilities
│       ├── __init__.py
│       ├── base.py           # Base data models
│       ├── expense.py        # Expense-related models
│       ├── processors.py     # Data processing utilities
│       ├── date_utils.py     # Date parsing utilities
│       └── json_utils.py     # JSON handling utilities
├── logs/                      # Application logs
├── credentials/               # Service credentials
└── README.md                  # This file
```

## 🚀 Quick Start

### **1. Prerequisites**

```bash
# Python 3.9 or higher
python --version

# Install dependencies
pip install -r requirements.txt
```

### **2. Environment Setup**

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

### **3. Required Environment Variables**

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather

# Google Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash-exp

# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS_PATH=./credentials/google_credentials.json
GOOGLE_SHEETS_ID=your_spreadsheet_id
SHEETS_RANGE=Sheet1!A:H

# Application Settings (Optional)
LOG_LEVEL=INFO
ENABLE_DEBUG=false
MAX_RETRIES=3
AGENT_TIMEOUT=30
```

### **4. Service Setup**

#### **🤖 Telegram Bot:**
1. Message @BotFather on Telegram
2. Create new bot: `/newbot`
3. Save the token to `.env`

#### **🧠 Google Gemini AI:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create API key
3. Save to `.env`

#### **📊 Google Sheets:**
1. Create Google Cloud Project
2. Enable Google Sheets API
3. Create Service Account
4. Download credentials JSON
5. Place in `./credentials/` folder
6. Share your Google Sheet with service account email

### **5. Run the Application**

```bash
python main.py
```

Expected output:
```
╔══════════════════════════════════════╗
║    🤖 AI-POWERED GROCERY TRACKING    ║
╚══════════════════════════════════════╝
🚀 Starting Telegram Bot with Agent System...
🎯 System ready! Bot is now active...
```

## 💡 Usage Guide

### **📱 Bot Commands**

```
/start  - Welcome message and system overview
/help   - Detailed usage guide and examples
/test   - Run system functionality tests
/status - Check system health and diagnostics
```

### **📸 Receipt Processing**

Simply send a photo of your grocery receipt to the bot:

1. **Upload receipt image** 📷
2. **AI analyzes** with Gemini Vision 🧠
3. **Extracts items, prices, store info** 📊
4. **Processes and formats data** ⚙️
5. **Saves to Google Sheets** 💾

**Supported formats:**
- Clear, well-lit receipt photos
- Various receipt layouts and formats
- Multiple items per receipt
- Different date formats

### **💬 Text Expense Processing**

Send natural language expense descriptions:

**Examples:**
```
"Milk ₹60, Bread ₹40, Eggs ₹80"
"Bought vegetables: Tomatoes ₹30, Onions ₹25"
"Grocery shopping cost ₹500 - Apples 2kg, Rice 5kg"
"Spent ₹150 on fruits today"
```

**Processing:**
1. **Text analysis** with Gemini NLP 🧠
2. **Smart keyword detection** 🔍
3. **Price and item extraction** 💰
4. **Automatic categorization** 📋
5. **Data formatting and storage** 💾

## 📊 Data Output Format

Data is automatically saved to Google Sheets with the following structure:

| Date | Original Item Name | Item Name | Pieces | Unit Size | Total Quantity | Price | Value |
|------|-------------------|-----------|---------|-----------|----------------|-------|-------|
| 2025-06-19 | E FR DRAKSHE-500g | Grapes | 1 | 500g | 0.5kg | 60.00 | 60.00 |
| 2025-06-19 | E LIME-5pcs | Lime | 1 | 5pcs | 5pcs | 30.00 | 30.00 |

### **Data Processing Features:**
- **Smart name cleaning** - Removes codes and standardizes names
- **Package size extraction** - Handles kg, g, pcs, liters
- **Unit conversion** - Automatic g→kg conversion when appropriate
- **Price calculation** - Per-unit and total price computation
- **Date handling** - Multiple date format support

## 🔧 System Components

### **🧠 Agent System**

#### **Agent Manager (Singleton)**
- Central orchestrator for all agents
- Routes requests to appropriate specialized agents
- Provides system health monitoring
- Handles agent registration and discovery

#### **Receipt Processing Agent**
- Specializes in image-based receipt analysis
- Coordinates with Gemini Vision API
- Handles complex receipt formats
- Extracts store information and dates

#### **Text Expense Agent**
- Processes natural language expense input
- Uses advanced NLP for context understanding
- Handles various text formats and languages
- Smart keyword and price detection

### **🔧 Tool System**

#### **Process Receipt Tool**
- Image preprocessing and optimization
- Gemini Vision API integration
- JSON response parsing and validation
- Error handling and retries

#### **Extract Text Expense Tool**
- Natural language processing
- Context-aware text analysis
- Price and quantity extraction
- Item categorization

#### **Save to Sheets Tool**
- Data formatting and validation
- Google Sheets API integration
- Batch processing for efficiency
- Automatic header creation

#### **Tool Registry**
- Dynamic tool discovery
- Execution management
- Error handling and logging
- Tool lifecycle management

### **🏗️ Services Layer**

#### **Gemini Service (Singleton)**
- Google Gemini AI integration
- Both vision and text processing
- Connection pooling and management
- Rate limiting and error handling

#### **Google Sheets Service (Singleton)**
- Google Sheets API integration
- Async operations for performance
- Automatic authentication handling
- Data validation and formatting

#### **Prompt Service**
- Centralized prompt management
- Template system for AI prompts
- Validation and optimization
- Version control for prompts

#### **Service Factory**
- Dependency injection container
- Service lifecycle management
- Health monitoring
- Configuration management

### **📊 Data Models**

#### **Expense Models**
- `ExpenseItem` - Individual expense items
- `ExpenseData` - Complete expense records
- `ProcessedItem` - Sheet-ready data format

#### **Processing Utilities**
- `ItemProcessor` - Smart data cleaning and formatting
- `DateParser` - Multi-format date handling
- `JSONExtractor` - AI response parsing

## ⚙️ Configuration

The system uses an enhanced configuration system with comprehensive validation:

### **Basic Configuration**
```python
from config import config

# Access configuration
model = config.gemini_model
timeout = config.agent_timeout
debug = config.enable_debug
```

### **Environment-Aware Settings**
```python
if config.is_production():
    # Production-specific logic
    pass

# Feature flags
if config.enable_analytics:
    # Analytics code
    pass
```

### **Available Settings**

#### **AI Configuration**
- `gemini_model` - AI model selection
- `gemini_temperature` - Response creativity (0.0-2.0)
- `gemini_max_tokens` - Maximum response length

#### **Performance Settings**
- `cache_size` - Memory cache size
- `cache_ttl` - Cache expiration time
- `connection_pool_size` - HTTP connection pool
- `max_concurrent_agents` - Parallel processing limit

#### **Security Settings**
- `allowed_users` - User whitelist
- `rate_limit_per_user` - Rate limiting
- `enable_user_whitelist` - Access control

#### **Feature Flags**
- `enable_analytics` - Usage analytics
- `enable_backup` - Data backup
- `enable_health_checks` - System monitoring

## 🔍 Monitoring & Debugging

### **Logging System**
```bash
# View real-time logs
tail -f logs/grocery_bot.log

# Check for errors
grep "ERROR" logs/grocery_bot.log

# Monitor agent activity
grep "Agent" logs/grocery_bot.log
```

### **Health Monitoring**
```bash
# System status via bot
/status

# Test functionality
/test

# Check configuration
python -c "from config import config; print(config.get_summary())"
```

### **Debug Mode**
```env
# Enable in .env
ENABLE_DEBUG=true
LOG_LEVEL=DEBUG
```

## 🧪 Testing

### **Manual Testing**
- Use `/test` command in Telegram bot
- Send test receipt images
- Try various text expense formats

### **System Validation**
```python
# Test configuration
python -c "from config import config; config.validate()"

# Test services
python -c "from src.services import service_factory; print(service_factory.get_service_status())"

# Test individual components
python -c "from src.agents import AgentManager; import asyncio; print(asyncio.run(AgentManager().get_system_status()))"
```

## 🚀 Deployment

### **Local Development**
```bash
python main.py
```

### **Docker Deployment**
```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f grocery-bot
```

### **Production Considerations**
- Set `ENVIRONMENT=production` in `.env`
- Use proper logging levels (`WARNING` or `ERROR`)
- Configure rate limiting and user whitelisting
- Set up monitoring and health checks
- Use secure credential management

## 🔒 Security

### **Credentials Management**
- Never commit `.env` files to version control
- Use service accounts with minimal permissions
- Rotate API keys regularly
- Monitor API usage and costs

### **Data Privacy**
- Receipt images processed in memory only
- No persistent image storage
- Google Sheets access via service account
- Telegram messages not permanently stored

### **Access Control**
```env
# Enable user whitelisting
ENABLE_USER_WHITELIST=true
ALLOWED_USERS=user1,user2,user3

# Set rate limits
RATE_LIMIT_PER_USER=50
```

## 🔧 Troubleshooting

### **Common Issues**

#### **Configuration Errors**
```bash
# Check environment variables
python -c "from config import config; config.validate()"

# Verify file paths
ls -la credentials/google_credentials.json
```

#### **API Connection Issues**
```bash
# Test Gemini API
curl -H "Authorization: Bearer $GEMINI_API_KEY" \
     https://generativelanguage.googleapis.com/v1beta/models

# Test Telegram Bot
curl https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe
```

#### **Google Sheets Access**
- Verify service account has access to the spreadsheet
- Check that the sheet ID is correct
- Ensure the service account email has Editor permissions

### **Debug Commands**
```python
# Test individual services
python -c "from src.services import GeminiService; print(GeminiService().call('test'))"

# Test agent system
python -c "from src.agents import AgentManager; import asyncio; print(asyncio.run(AgentManager().get_system_status()))"

# Test tool system
python -c "from src.tools import ToolRegistry; registry = ToolRegistry(); print(registry.list_tools())"
```

## 📈 Performance Optimization

### **Built-in Optimizations**
- **Singleton Services** - Reduced memory usage and faster access
- **Async Processing** - Non-blocking I/O operations
- **Connection Pooling** - Efficient API usage
- **Caching** - Configurable memory caching
- **Batch Processing** - Efficient Google Sheets updates

### **Configuration Tuning**
```env
# Performance settings
CACHE_SIZE=2000
CONNECTION_POOL_SIZE=20
MAX_CONCURRENT_AGENTS=10
SHEETS_BATCH_SIZE=100
```

## 🤝 Contributing

### **Development Setup**
```bash
# Clone repository
git clone <repository-url>
cd grocery_bot_system

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your credentials

# Run tests
python -m pytest tests/ # (when tests are added)
```

### **Code Style**
- Follow PEP 8 guidelines
- Use type hints throughout
- Add comprehensive docstrings
- Maintain test coverage

### **Adding New Components**

#### **New Tool:**
```python
# src/tools/my_new_tool.py
from .base import BaseTool

class MyNewTool(BaseTool):
    def __init__(self):
        super().__init__("my_tool", "Description")
    
    async def execute(self, **kwargs) -> str:
        # Implementation
        return "result"
```

#### **New Agent:**
```python
# src/agents/my_new_agent.py
from .base import BaseAgent

class MyNewAgent(BaseAgent):
    def __init__(self):
        super().__init__("My Agent", "Description", ["tool1", "tool2"])
    
    async def execute(self, **kwargs) -> AgentResult:
        # Implementation
        return AgentResult(success=True, message="Done")
```

## 📚 API Reference

### **Agent Manager**
```python
from src.agents import AgentManager

manager = AgentManager()

# Process receipt
result = await manager.process_receipt_image(image_data, date)

# Process text
result = await manager.process_text_expense(text, date)

# System status
status = await manager.get_system_status()
```

### **Service Factory**
```python
from src.services import service_factory, GeminiService

# Get services
gemini = service_factory.get_service(GeminiService)

# Health checks
health = await service_factory.health_check_all()
```

### **Configuration**
```python
from config import config, get_config, is_debug_enabled

# Access config
model = config.gemini_model
debug = is_debug_enabled()

# Configuration summary
print(config.get_summary())
```

## 🎯 Roadmap

### **Current Version: v1.0**
- ✅ Modular architecture
- ✅ Receipt and text processing
- ✅ Google Sheets integration
- ✅ Production-ready features

### **Next Steps: v2.0 (Agentic AI)**
- 🔄 **Planning** - Dynamic reasoning and planning
- 🤖 **True Agency** - Goal-oriented behavior
- 🧠 **Memory** - Learning from interactions
- 🔧 **Tool Selection** - Dynamic tool choosing
- 🤝 **Multi-Agent** - Agent collaboration

### **Future Enhancements**
- 📊 Analytics dashboard
- 🌐 Web interface
- 📱 Mobile app
- 🔗 API endpoints
- 🗄️ Database support
- 🔄 Real-time sync

## 📞 Support

- **Issues**: Create GitHub issues for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check this README and inline documentation
- **Logs**: Always check `logs/grocery_bot.log` for troubleshooting

## 📄 License

[Add your license information here]

---

**🎉 Your AI-Powered Grocery Tracking System is ready!**

This system provides a solid foundation for expense tracking and is architecturally prepared for evolution into a true agentic AI system. The modular design ensures easy maintenance, testing, and extension.

For questions or contributions, please refer to the troubleshooting section or create an issue in the repository.