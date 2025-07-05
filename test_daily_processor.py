import os
import sys
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from processors.email_daily_processor import EmailDailyProcessor
from config import DEFAULT_MODEL, UNSUBSCRIBE_KEYWORDS

def test_configuration():
    """Test that configuration is properly loaded"""
    print("🧪 Testing configuration...")
    
    print(f"✅ Default model: {DEFAULT_MODEL}")
    print(f"✅ Unsubscribe keywords count: {len(UNSUBSCRIBE_KEYWORDS)}")
    print(f"✅ Sample unsubscribe keywords: {UNSUBSCRIBE_KEYWORDS[:3]}")
    
def test_environment_variables():
    """Test that required environment variables are set"""
    print("\n🧪 Testing environment variables...")
    
    load_dotenv()
    
    required_vars = ["EMAIL_ADDRESS", "EMAIL_PASSWORD", "OPENROUTER_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var}: Set")
        else:
            print(f"❌ {var}: Missing")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {missing_vars}")
        print("Please set these in your .env file before running Phase 1.1")
        return False
    
    return True

def test_processor():    
    if not test_environment_variables():
        print("❌ Cannot test daily processor without proper environment setup")
        return
    
    try:
        # Initialize the processor
        processor = EmailDailyProcessor()
        print("✅ EmailDailyProcessor initialized successfully")
        
        # Run the daily processing
        print("\n🚀 Running daily email processing...")
        processor.process_daily_emails()
        
    except Exception as e:
        print(f"❌ Daily processor test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests"""
    print("=" * 50)

    test_configuration()
    test_processor()

    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    main()
