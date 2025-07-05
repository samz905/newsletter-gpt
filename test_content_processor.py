import os
import sys
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from processors.daily_newsletter_processor import DailyNewsletterProcessor
from processors.batch_processor import BatchProcessor
from processors.sqlite_manager import SQLiteManager
from processors.content_processor import ContentProcessor
from config import DEFAULT_MODEL, APPROVED_GENRES, BATCH_SIZE

def test_configuration():
    """Test that configuration is properly loaded"""
    print("🧪 Testing configuration...")
    
    print(f"✅ Default model: {DEFAULT_MODEL}")
    print(f"✅ Approved genres count: {len(APPROVED_GENRES)}")
    print(f"✅ Batch size: {BATCH_SIZE}")
    print(f"✅ Sample genres: {APPROVED_GENRES[:3]}")

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
        print("Please set these in your .env file before running")
        return False
    
    return True

def test_batch_processor():
    """Test the BatchProcessor component"""
    print("\n🧪 Testing BatchProcessor...")
    
    # Create test newsletters
    test_newsletters = [
        {
            'subject': 'Tech Weekly: AI Breakthroughs',
            'sender': 'tech@example.com',
            'date': '2024-01-15',
            'body': 'This week in AI: OpenAI releases new models, Google announces Gemini updates, and Microsoft integrates AI into Office. The future of work is changing rapidly with these AI advancements. Key developments include improved language models, better reasoning capabilities, and more efficient training methods. Companies are investing heavily in AI infrastructure.'
        },
        {
            'subject': 'Business Insights: Market Trends',
            'sender': 'business@example.com', 
            'date': '2024-01-15',
            'body': 'Market analysis shows strong growth in tech sector. Key trends include: cloud adoption, remote work tools, and cybersecurity investments. Companies are pivoting to digital-first strategies. The quarterly earnings show consistent growth across major tech companies. Investors are focusing on sustainable growth and innovation.'
        }
    ]
    
    try:
        processor = BatchProcessor()
        print(f"✅ BatchProcessor initialized with model: {processor.model}")
        
        # Test batch processing (this will make actual LLM calls)
        print("🤖 Testing LLM batch processing (this may take time)...")
        results = processor.process_newsletter_batches(test_newsletters)
        
        if results:
            print(f"✅ Batch processing successful: {len(results)} newsletters processed")
            for result in results:
                print(f"   - {result['subject']} -> {result['genre']}")
            return True
        else:
            print("❌ Batch processing failed")
            return False
            
    except Exception as e:
        print(f"❌ BatchProcessor test failed: {e}")
        return False

def test_sqlite_manager():
    """Test the SQLiteManager component"""
    print("\n🧪 Testing SQLiteManager...")
    
    try:
        manager = SQLiteManager()
        print("✅ SQLiteManager initialized")
        
        # Test connection
        if manager.connect():
            print("✅ Database connection successful")
            
            # Test table creation
            if manager.create_tables():
                print("✅ Database tables created successfully")
                
                # Test with sample data
                test_data = [
                    {
                        'sender': 'test@example.com',
                        'subject': 'Test Newsletter',
                        'summary': 'This is a test summary',
                        'source': 'https://test.com',
                        'date': '2024-01-15',
                        'genre': 'Technology',
                        'word_count': 5
                    }
                ]
                
                # Test storing data
                if manager.store_processed_newsletters(test_data):
                    print("✅ Newsletter storage successful")
                    
                    # Test retrieving stats
                    stats = manager.get_database_stats()
                    print(f"✅ Database stats: {stats}")
                    
                    manager.disconnect()
                    return True
                else:
                    print("❌ Newsletter storage failed")
                    manager.disconnect()
                    return False
            else:
                print("❌ Table creation failed")
                manager.disconnect()
                return False
        else:
            print("❌ Database connection failed")
            return False
            
    except Exception as e:
        print(f"❌ SQLiteManager test failed: {e}")
        return False

def test_content_processor():
    """Test the ContentProcessor component"""
    print("\n🧪 Testing ContentProcessor...")
    
    # Test newsletter candidates (from Phase 1.1 format)
    test_candidates = [
        {
            'id': '1',
            'subject': 'Tech Weekly: AI Breakthroughs',
            'sender': 'tech@example.com',
            'date': 'Mon, 15 Jan 2024 10:00:00 +0000',
            'body': 'This week in AI: OpenAI releases new models, Google announces Gemini updates, and Microsoft integrates AI into Office. The future of work is changing rapidly with these AI advancements. Key developments include improved language models, better reasoning capabilities, and more efficient training methods.'
        }
    ]
    
    try:
        processor = ContentProcessor()
        print("✅ ContentProcessor initialized")
        
        # Test the complete workflow
        print("🚀 Testing complete workflow...")
        success = processor.process_newsletter_candidates(test_candidates)
        
        if success:
            print("✅ Workflow completed successfully")
            
            # Get processing stats
            stats = processor.get_processing_stats()
            print(f"✅ Processing stats: {stats}")
            return True
        else:
            print("❌ Workflow failed")
            return False
            
    except Exception as e:
        print(f"❌ ContentProcessor test failed: {e}")
        return False

def test_daily_newsletter_processor():
    """Test the complete DailyNewsletterProcessor"""
    print("\n🧪 Testing DailyNewsletterProcessor...")
    
    try:
        processor = DailyNewsletterProcessor()
        print("✅ DailyNewsletterProcessor initialized")
        
        # Test configuration
        if processor.test_configuration():
            print("✅ Configuration test passed")
            
            # Test the complete daily processing workflow
            print("🚀 Testing complete daily processing workflow...")
            print("📧 This will fetch real emails from your Gmail and process them with LLM")
            
            # Ask user for confirmation
            response = input("\nDo you want to run the complete daily processing test? (y/N): ")
            if response.lower() != 'y':
                print("⏭️  Skipping complete daily processing test")
                return True
            
            results = processor.run_daily_processing()
            
            if results['success']:
                print("✅ Complete daily processing test PASSED!")
                print(f"📊 Results: {results}")
                return True
            else:
                print("❌ Complete daily processing test FAILED!")
                print(f"📊 Results: {results}")
                return False
        else:
            print("❌ Configuration test failed")
            return False
            
    except Exception as e:
        print(f"❌ DailyNewsletterProcessor test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Implementation")
    print("=" * 60)
    
    # Basic configuration tests
    test_configuration()
    
    if not test_environment_variables():
        print("\n❌ Environment variables not properly configured")
        print("Please set up your .env file before running tests")
        return
    
    # Component tests
    test_results = []
    
    # Test SQLiteManager first (no LLM calls)
    test_results.append(("SQLiteManager", test_sqlite_manager()))
    
    # Test BatchProcessor (makes LLM calls)
    response = input("\nDo you want to test BatchProcessor? This will make LLM calls. (y/N): ")
    if response.lower() == 'y':
        test_results.append(("BatchProcessor", test_batch_processor()))
    else:
        print("⏭️  Skipping BatchProcessor test")
        test_results.append(("BatchProcessor", "skipped"))
    
    # Test ContentProcessor (makes LLM calls)
    response = input("\nDo you want to test ContentProcessor? This will make LLM calls. (y/N): ")
    if response.lower() == 'y':
        test_results.append(("ContentProcessor", test_content_processor()))
    else:
        print("⏭️  Skipping ContentProcessor test")
        test_results.append(("ContentProcessor", "skipped"))
    
    # Test complete daily processor (fetches emails + makes LLM calls)
    test_results.append(("DailyNewsletterProcessor", test_daily_newsletter_processor()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in test_results:
        if result == "skipped":
            print(f"⏭️  {test_name}: SKIPPED")
        elif result:
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
    
    passed_tests = sum(1 for _, result in test_results if result is True)
    total_tests = len([r for _, r in test_results if r != "skipped"])
    
    print(f"\n📊 Tests passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  Some tests failed - check configuration and try again")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 