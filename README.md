# Newsletter GPT

Transform your newsletter subscriptions into intelligent weekly digests using AI with full automation and Notion integration.

## Overview

Newsletter GPT is a **production-ready** automated system that:
- 🕗 **Daily at 8 PM**: Fetches and processes your newsletter subscriptions
- 🧠 **AI Processing**: Uses OpenRouter + Gemini for intelligent summarization
- 📊 **Weekly Digests**: Generates comprehensive summaries every Sunday at 7 AM
- 📄 **Notion Integration**: Publishes beautiful weekly digests to Notion
- 🗄️ **Database Storage**: Maintains structured history in SQLite

## Architecture

```
⏰ Scheduler → 📧 Email Ingestion → 🧠 AI Processing → 🗄️ SQLite → 📊 Weekly Digest → 📄 Notion
```

## ✨ Features

### Core Functionality
- **🔄 Full Automation**: Runs daily and weekly without intervention
- **🧠 AI Batch Processing**: Efficient LLM processing (10 newsletters per call)
- **📊 Genre Classification**: 15 approved genres for organized content
- **📅 Weekly Digests**: Intelligent summaries grouped by genre
- **🗄️ SQLite Database**: Persistent storage with proper indexing
- **⚡ Rate Limiting**: Smart API usage to stay within limits

### Production Features
- **🚀 Production Deployment**: Complete Ubuntu server setup
- **📋 Systemd Service**: Runs as system service with auto-restart
- **📊 Monitoring**: Comprehensive logging and status monitoring
- **🔒 Security**: Proper user isolation and file permissions
- **💾 Backup**: Automated database and log backups
- **📧 Notifications**: Error alerts and job completion notifications

### Notion Integration
- **📄 Rich Formatting**: Beautiful weekly digest pages
- **🎨 Emojis & Sections**: Genre-specific emojis and organized sections
- **📈 Statistics**: Newsletter counts and processing metrics
- **🔗 Source Links**: Links to original newsletters
- **📅 Date Ranges**: Clear weekly date ranges

## 🚀 Quick Start

### Option 1: Automated Setup
```bash
# Local development
chmod +x quick_start.sh
./quick_start.sh

# Production deployment (Ubuntu)
sudo chmod +x deploy/install.sh
sudo ./deploy/install.sh
```

### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with your credentials
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
OPENROUTER_API_KEY=your_openrouter_key
NOTION_TOKEN=your_notion_integration_token
NOTION_DATABASE_ID=your_notion_database_id

# Test components
python app.py test-components

# Start the application
python app.py start
```

## 📱 Usage

### Production Commands
```bash
# Start/stop service
sudo systemctl start newsletter-gpt
sudo systemctl stop newsletter-gpt
sudo systemctl restart newsletter-gpt

# Check status and logs
sudo systemctl status newsletter-gpt
journalctl -u newsletter-gpt -f
```

### Development Commands
```bash
# Application control
python app.py start                 # Start full scheduler
python app.py test-daily           # Run daily processing manually
python app.py test-weekly          # Run weekly digest manually
python app.py test-components      # Test all components
python app.py status               # Show application status

# Component testing
python processors/daily_newsletter_processor.py  # Test daily workflow
python processors/weekly_digest_generator.py     # Test weekly digest
python processors/notion_publisher.py            # Test Notion integration
```

## 🏗️ Architecture

### Core Components
- **📧 Email Processing**: IMAP connection, email parsing, content cleaning
- **🧠 Batch Processor**: AI-powered summarization and genre classification
- **🗄️ SQLite Manager**: Database operations and document storage
- **📊 Weekly Generator**: Digest creation and formatting
- **📄 Notion Publisher**: Rich formatting and API integration
- **⏰ Scheduler**: Automated daily/weekly job execution

### Configuration
- **⚙️ Centralized Config**: All settings in `config.py`
- **🔧 Environment Variables**: Secure credential management
- **📊 Rate Limiting**: Configurable API limits and retry logic
- **🧪 Test Mode**: Faster intervals for development

## 🎯 Status: 🎉 ALL PHASES COMPLETE!

- ✅ **Phase 1**: Foundation & Modularization
- ✅ **Phase 2**: Daily Processing System  
- ✅ **Phase 3**: Weekly Digest System
- ✅ **Phase 4**: Integration & Deployment (Scheduler + Notion + Production)

## 📋 Requirements

### System Requirements
- **OS**: Ubuntu 20.04+ (or compatible Linux)
- **Python**: 3.9+
- **Memory**: 512MB+ available
- **Storage**: 1GB+ free space

### API Requirements
- **📧 Gmail**: Account with app password enabled
- **🧠 OpenRouter**: API key for Gemini access
- **📄 Notion**: Integration token and database ID

### Python Dependencies
All dependencies are listed in `requirements.txt` and installed automatically.

## 📂 Project Structure

```
newsletter-gpt/
├── app.py                          # Main application entry point
├── quick_start.sh                  # Local development setup
├── deploy/install.sh               # Production deployment
├── processors/
│   ├── scheduler.py                # APScheduler automation
│   ├── notion_publisher.py         # Notion integration
│   ├── daily_newsletter_processor.py
│   ├── weekly_digest_generator.py
│   └── ...
├── email_processing/               # Email fetching and parsing
├── config.py                       # Centralized configuration
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Email Configuration
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# OpenRouter API (for Gemini)
OPENROUTER_API_KEY=your_openrouter_api_key

# Notion Integration
NOTION_TOKEN=your_notion_integration_token
NOTION_DATABASE_ID=your_notion_database_id

# Optional: Database Configuration
NEWSLETTER_DB_PATH=newsletter_data.db
LOG_LEVEL=INFO
```

### Scheduling
- **📅 Daily Processing**: Every day at 8:00 PM
- **📊 Weekly Digest**: Every Sunday at 7:00 AM
- **⚙️ Configurable**: Modify in `processors/scheduler.py`

## 🛠️ Deployment

### Local Development
Perfect for testing and development on your local machine.

### Production Server
Full Ubuntu server deployment with:
- **🔧 Systemd Service**: Automatic startup and restart
- **📊 Monitoring**: Comprehensive logging and status tracking
- **🔒 Security**: Proper user isolation and permissions
- **💾 Backups**: Automated database and log backups
- **🔄 Log Rotation**: Prevents disk space issues

## 📊 Monitoring

### Logs
- **📋 Application**: `logs/newsletter_gpt.log`
- **❌ Errors**: `logs/newsletter_gpt_errors.log`
- **🔄 System**: `journalctl -u newsletter-gpt -f`

### Status Monitoring
- **⚡ Real-time**: `python app.py status`
- **📊 System**: `systemctl status newsletter-gpt`
- **💾 Resources**: Built-in memory and disk monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- **OpenRouter**: For free Gemini API access
- **Notion**: For beautiful digest publishing
- **APScheduler**: For reliable job scheduling
- **All contributors**: Who helped build this system

---

**Ready to transform your newsletter chaos into organized intelligence?** 🚀

Get started with: `./quick_start.sh`