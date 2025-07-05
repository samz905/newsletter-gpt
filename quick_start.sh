#!/bin/bash

# Newsletter GPT Quick Start Script
# For local development and testing

set -e

echo "🚀 Newsletter GPT Quick Start"
echo "============================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create a .env file with your configuration."
    echo "Example:"
    echo ""
    echo "EMAIL_ADDRESS=your_email@gmail.com"
    echo "EMAIL_PASSWORD=your_app_password"
    echo "OPENROUTER_API_KEY=your_openrouter_api_key"
    echo "NOTION_TOKEN=your_notion_integration_token"
    echo "NOTION_DATABASE_ID=your_notion_database_id"
    echo ""
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Initialize database
echo "🗄️ Initializing database..."
python -c "
from processors.sqlite_manager import SQLiteManager
db = SQLiteManager()
db.connect()
db.create_tables()
db.disconnect()
print('✅ Database initialized successfully')
"

# Test components
echo "🧪 Testing components..."
if python app.py test-components; then
    echo "✅ All components working!"
else
    echo "❌ Component tests failed. Please check your .env configuration."
    exit 1
fi

echo ""
echo "🎉 Quick start complete!"
echo ""
echo "Available commands:"
echo "  python app.py start                 - Start the full scheduler"
echo "  python app.py test-daily           - Run daily processing manually"
echo "  python app.py test-weekly          - Run weekly digest manually"
echo "  python app.py test-components      - Test all components"
echo "  python app.py status               - Show application status"
echo ""
echo "Development shortcuts:"
echo "  python processors/daily_newsletter_processor.py     - Test daily processor"
echo "  python processors/weekly_digest_generator.py        - Test weekly generator"
echo "  python processors/notion_publisher.py               - Test Notion publisher"
echo "  python processors/scheduler.py --test-daily         - Test scheduler daily job"
echo "  python processors/scheduler.py --test-weekly        - Test scheduler weekly job"
echo ""
echo "🚀 Ready to go! Start with: python app.py start" 