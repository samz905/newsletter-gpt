import os
import sys
import time
import sqlite3
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from config import *
from processors.daily_newsletter_processor import DailyNewsletterProcessor
from processors.weekly_digest_generator import WeeklyDigestGenerator
from processors.notion_publisher import NotionPublisher
from email_processing.email_fetcher import EmailFetcher
from email_processing.email_parser import EmailParser
from processors.content_cleaner import ContentCleaner


def test_config():
    """Test configuration and environment variables"""
    print("🔧 Testing Configuration...")
    
    required_vars = [
        'EMAIL_ADDRESS',
        'EMAIL_PASSWORD', 
        'OPENROUTER_API_KEY',
        'NOTION_TOKEN',
        'NOTION_DATABASE_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            print(f"✅ {var}: {'*' * min(len(value), 10)}")
    
    if missing_vars:
        print(f"❌ Missing variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ Configuration test passed")
    return True


def test_email_processing():
    """Test email processing components"""
    print("\n📧 Testing Email Processing...")
    
    try:
        # Test email fetcher with environment variables
        fetcher = EmailFetcher(
            email_address=os.getenv('EMAIL_ADDRESS'),
            password=os.getenv('EMAIL_PASSWORD')
        )
        print("✅ Email fetcher initialized")
        
        # Test content cleaner (doesn't need connection)
        cleaner = ContentCleaner()
        
        # Test basic cleaning
        test_newsletter = {
            'subject': 'Test Newsletter',
            'body': """
            <html>
            <body>
            <h1>Test Newsletter</h1>
            <p>This is a test newsletter with <a href="http://example.com">links</a>.</p>
            <div>Some additional content here.</div>
            </body>
            </html>
            """
        }
        
        cleaned_newsletters = cleaner.clean_newsletters([test_newsletter])
        if cleaned_newsletters and len(cleaned_newsletters) > 0:
            cleaned_body = cleaned_newsletters[0].get('cleaned_body', '')
            if cleaned_body:
                print("✅ Content cleaner working")
            else:
                print("❌ Content cleaner failed - no cleaned_body")
                return False
        else:
            print("❌ Content cleaner failed - no results")
            return False
        
        print("✅ Email processing test passed")
        return True
        
    except Exception as e:
        print(f"❌ Email processing test failed: {e}")
        return False


def test_daily_processing():
    """Test daily newsletter processing"""
    print("\n📊 Testing Daily Processing...")
    
    try:
        # Check database stats first
        db_path = Path(DATABASE_PATH)
        if db_path.exists():
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # Get newsletter stats
            cursor.execute("SELECT COUNT(*) FROM newsletters")
            total_newsletters = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT genre) FROM newsletters")
            unique_genres = cursor.fetchone()[0]
            
            print(f"📊 Database stats: {total_newsletters} newsletters, {unique_genres} genres")
            conn.close()
        else:
            print("📊 Database not found - will be created on first run")
        
        # Test daily processor
        processor = DailyNewsletterProcessor()
        print("✅ Daily processor initialized")
        
        # We won't run actual processing to avoid hitting email servers
        print("✅ Daily processing test passed (initialization check)")
        return True
        
    except Exception as e:
        print(f"❌ Daily processing test failed: {e}")
        return False


def test_weekly_digest():
    """Test weekly digest generation"""
    print("\n📝 Testing Weekly Digest Generation...")
    
    try:
        generator = WeeklyDigestGenerator()
        print("✅ Weekly digest generator initialized")
        
        # Test digest structure without actual generation
        print("✅ Weekly digest test passed (initialization check)")
        return True
        
    except Exception as e:
        print(f"❌ Weekly digest test failed: {e}")
        return False


def test_notion_integration():
    """Test Notion integration"""
    print("\n📄 Testing Notion Integration...")
    
    try:
        publisher = NotionPublisher()
        print("✅ Notion publisher initialized")
        
        # Test connection
        if publisher.test_connection():
            print("✅ Notion connection successful")
        else:
            print("❌ Notion connection failed")
            return False
        
        # Test emoji mapping
        tech_emoji = publisher._get_genre_emoji('Technology')
        biz_emoji = publisher._get_genre_emoji('Business')
        science_emoji = publisher._get_genre_emoji('Science')
        
        print(f"✅ Genre emojis: Technology {tech_emoji}, Business {biz_emoji}, Science {science_emoji}")
        
        print("✅ Notion integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Notion integration test failed: {e}")
        return False


def test_fastapi_server():
    """Test FastAPI server endpoints"""
    print("\n🌐 Testing FastAPI Server...")
    
    base_url = "http://localhost:8000"
    
    try:
        # Test root endpoint
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Server root endpoint working")
        else:
            print(f"❌ Server root endpoint failed: {response.status_code}")
            return False
        
        # Test status endpoint
        response = requests.get(f"{base_url}/status", timeout=5)
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ Status endpoint working: {status_data}")
        else:
            print(f"❌ Status endpoint failed: {response.status_code}")
            return False
        
        print("✅ FastAPI server test passed")
        return True
        
    except requests.exceptions.ConnectionError:
        print("⚠️ FastAPI server not running - start with 'python app.py'")
        return False
    except Exception as e:
        print(f"❌ FastAPI server test failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("🧪 Running Newsletter GPT Test Suite...")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_config),
        ("Email Processing", test_email_processing),
        ("Daily Processing", test_daily_processing),
        ("Weekly Digest", test_weekly_digest),
        ("Notion Integration", test_notion_integration),
        ("FastAPI Server", test_fastapi_server),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Newsletter GPT is ready to use.")
    else:
        print("⚠️ Some tests failed. Check the output above.")
    
    return passed == total


def manual_job_menu():
    """Interactive menu for manual job execution"""
    print("\n🔧 Manual Job Execution Menu")
    print("=" * 30)
    print("1. Run Daily Processing")
    print("2. Run Weekly Digest")
    print("3. Test Notion Connection")
    print("4. Trigger via API (Daily)")
    print("5. Trigger via API (Weekly)")
    print("6. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            print("\n🚀 Running Daily Processing...")
            try:
                processor = DailyNewsletterProcessor()
                result = processor.run_daily_processing()
                if result.get('success'):
                    print(f"✅ Daily processing completed: {result}")
                else:
                    print(f"❌ Daily processing failed: {result}")
            except Exception as e:
                print(f"❌ Daily processing error: {e}")
        
        elif choice == '2':
            print("\n🚀 Running Weekly Digest...")
            try:
                generator = WeeklyDigestGenerator()
                result = generator.generate_weekly_digest()
                if result:
                    print(f"✅ Weekly digest generated: {result}")
                else:
                    print("❌ Weekly digest generation failed")
            except Exception as e:
                print(f"❌ Weekly digest error: {e}")
        
        elif choice == '3':
            print("\n🚀 Testing Notion Connection...")
            try:
                publisher = NotionPublisher()
                if publisher.test_connection():
                    print("✅ Notion connection successful")
                else:
                    print("❌ Notion connection failed")
            except Exception as e:
                print(f"❌ Notion connection error: {e}")
        
        elif choice == '4':
            print("\n🚀 Triggering Daily Job via API...")
            try:
                response = requests.post("http://localhost:8000/jobs/daily", timeout=10)
                if response.status_code == 200:
                    print(f"✅ Daily job triggered: {response.json()}")
                else:
                    print(f"❌ API call failed: {response.status_code}")
            except Exception as e:
                print(f"❌ API call error: {e}")
        
        elif choice == '5':
            print("\n🚀 Triggering Weekly Job via API...")
            try:
                response = requests.post("http://localhost:8000/jobs/weekly", timeout=10)
                if response.status_code == 200:
                    print(f"✅ Weekly job triggered: {response.json()}")
                else:
                    print(f"❌ API call failed: {response.status_code}")
            except Exception as e:
                print(f"❌ API call error: {e}")
        
        elif choice == '6':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1-6.")


def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == '--manual':
        manual_job_menu()
    else:
        success = run_all_tests()
        
        if success:
            print("\n🎮 Want to run manual jobs? Run: python test_workflow.py --manual")


if __name__ == "__main__":
    main() 