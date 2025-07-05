#!/usr/bin/env python3
"""
Test script for Complete Real Workflow
Tests the complete workflow: real email fetching → filtering → 10 newsletters → LLM processing → summaries/genres
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from processors.daily_newsletter_processor import DailyNewsletterProcessor
from processors.content_processor import ContentProcessor
from config import DEFAULT_MODEL, BATCH_SIZE

def test_configuration():
    """Test that configuration is properly loaded"""
    print("🧪 Testing configuration...")
    
    print(f"✅ Default model: {DEFAULT_MODEL}")
    print(f"✅ Batch size: {BATCH_SIZE}")
    
def test_environment_variables():
    """Test that required environment variables are set"""
    print("\n🧪 Testing environment variables...")
    
    load_dotenv()
    
    required_vars = ["OPENROUTER_API_KEY", "EMAIL_ADDRESS", "EMAIL_PASSWORD"]  # All vars needed for real workflow
    missing_vars = []
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var}: Set")
        else:
            print(f"❌ {var}: Missing")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {missing_vars}")
        print("Please set these in your .env file")
        return False
    
    return True

def create_test_newsletters():
    """Create 10 test newsletters for batch processing"""
    return [
        {
            'id': '1',
            'subject': 'Tech Weekly: AI Breakthroughs and Machine Learning Trends',
            'sender': 'tech@example.com',
            'date': 'Mon, 15 Jan 2024 10:00:00 +0000',
            'body': 'This week in AI: OpenAI releases new models with improved reasoning capabilities, Google announces Gemini updates with better multimodal understanding, and Microsoft integrates AI deeper into Office suite. The future of work is changing rapidly with these AI advancements. Key developments include improved language models, better reasoning capabilities, more efficient training methods, and breakthrough applications in code generation and scientific research.'
        },
        {
            'id': '2', 
            'subject': 'Business Insights: Market Trends and Economic Analysis',
            'sender': 'business@example.com',
            'date': 'Mon, 15 Jan 2024 11:00:00 +0000',
            'body': 'Market analysis shows strong growth in tech sector despite economic uncertainties. Key trends include cloud adoption acceleration, remote work tools proliferation, and cybersecurity investments surge. Companies are pivoting to digital-first strategies with renewed focus on operational efficiency. The quarterly earnings show consistent growth across major tech companies, with particular strength in AI and cloud services.'
        },
        {
            'id': '3',
            'subject': 'Health & Wellness: Latest Medical Breakthroughs',
            'sender': 'health@example.com', 
            'date': 'Mon, 15 Jan 2024 12:00:00 +0000',
            'body': 'Recent advances in personalized medicine are revolutionizing healthcare delivery. Gene therapy shows promising results for rare diseases, while AI-powered diagnostic tools improve early detection rates. Mental health awareness continues to grow with innovative digital therapeutic solutions. Preventive care strategies are becoming more sophisticated with wearable technology integration and predictive analytics.'
        },
        {
            'id': '4',
            'subject': 'Science Today: Climate Research and Environmental Solutions',
            'sender': 'science@example.com',
            'date': 'Mon, 15 Jan 2024 13:00:00 +0000', 
            'body': 'Climate scientists present new findings on carbon capture technologies and renewable energy efficiency. Ocean acidification research reveals concerning trends while also highlighting potential mitigation strategies. Biodiversity conservation efforts show mixed results globally, with some success stories in marine protected areas. Clean energy deployment accelerates with improved battery storage solutions.'
        },
        {
            'id': '5',
            'subject': 'Finance Focus: Investment Strategies and Market Outlook',
            'sender': 'finance@example.com',
            'date': 'Mon, 15 Jan 2024 14:00:00 +0000',
            'body': 'Portfolio diversification strategies adapt to changing market conditions with increased focus on ESG investments. Cryptocurrency markets show volatility patterns while institutional adoption continues steadily. Interest rate implications for various asset classes require careful consideration in current economic environment. Emerging markets present both opportunities and risks for international investors.'
        },
        {
            'id': '6',
            'subject': 'Education Evolution: Learning Technologies and Pedagogy',
            'sender': 'education@example.com', 
            'date': 'Mon, 15 Jan 2024 15:00:00 +0000',
            'body': 'Educational technology transforms traditional learning approaches with personalized adaptive systems. Online learning platforms continue evolution with improved engagement metrics and learning outcomes. Teacher training programs adapt to incorporate digital literacy and AI-assisted instruction methods. Student assessment methods evolve beyond standardized testing toward competency-based evaluation.'
        },
        {
            'id': '7',
            'subject': 'Culture & Society: Arts, Entertainment, and Social Trends',
            'sender': 'culture@example.com',
            'date': 'Mon, 15 Jan 2024 16:00:00 +0000',
            'body': 'Digital art and NFT markets mature with more sophisticated curation and valuation methods. Streaming services reshape entertainment consumption patterns with algorithm-driven content discovery. Social media platforms evolve privacy policies and content moderation approaches. Cultural preservation efforts leverage technology for archiving and accessibility initiatives.'
        },
        {
            'id': '8',
            'subject': 'Productivity Pro: Time Management and Efficiency Hacks',
            'sender': 'productivity@example.com',
            'date': 'Mon, 15 Jan 2024 17:00:00 +0000',
            'body': 'Remote work optimization strategies focus on communication tools and project management systems. Time blocking techniques gain popularity among knowledge workers seeking focus improvement. Automation tools reduce repetitive tasks while maintaining quality standards. Work-life balance approaches evolve with flexible scheduling and boundary-setting methodologies.'
        },
        {
            'id': '9',
            'subject': 'Personal Growth: Self-Development and Mindfulness Practices',
            'sender': 'growth@example.com',
            'date': 'Mon, 15 Jan 2024 18:00:00 +0000', 
            'body': 'Mindfulness meditation apps integrate with wearable devices for personalized wellness tracking. Goal-setting methodologies incorporate behavioral psychology insights for improved success rates. Habit formation research provides actionable frameworks for sustainable lifestyle changes. Community-based learning approaches enhance personal development outcomes through peer support and accountability.'
        },
        {
            'id': '10',
            'subject': 'Philosophy Corner: Ethics in Technology and Human Values',
            'sender': 'philosophy@example.com',
            'date': 'Mon, 15 Jan 2024 19:00:00 +0000',
            'body': 'AI ethics discussions examine algorithmic bias and fairness in automated decision-making systems. Privacy rights evolve with changing technology landscape and data collection practices. Human-AI collaboration raises questions about autonomy and decision-making authority. Digital wellness concepts address technology addiction and mindful consumption patterns.'
        }
    ]

def test_real_workflow_with_batch():
    """Test complete real workflow: fetch emails, filter, process 10 newsletters"""
    print("\n🧪 Testing Real Workflow with Email Fetching and Processing...")
    
    try:
        # Step 1: Fetch real emails from last 24 hours
        print("📧 Step 1: Fetching real emails from last 24 hours...")
        daily_processor = DailyNewsletterProcessor()
        
        # Get newsletter candidates (real emails, filtered)
        newsletter_candidates = daily_processor.daily_processor.process_daily_emails()
        
        if newsletter_candidates is None:
            print("❌ Failed to fetch emails")
            return False
            
        print(f"✅ Fetched {len(newsletter_candidates)} newsletter candidates")
        
        # Step 2: Take first 10 for testing (or all if less than 10)
        test_batch = newsletter_candidates[:10]
        print(f"📊 Using {len(test_batch)} newsletters for testing")
        
        if len(test_batch) == 0:
            print("⚠️  No newsletters found to process")
            return False
        
        # Step 3: Process through content processor
        print("🤖 Step 2: Processing newsletters through ContentProcessor...")
        success = daily_processor.content_processor.process_newsletter_candidates(test_batch)
        
        if not success:
            print("❌ Content processing failed")
            return False
            
        print("✅ Content processing completed successfully!")
        
        # Step 4: Show the results - summaries and genres
        print("\n📋 Step 3: Showing Results (Summaries and Genres)")
        print("=" * 80)
        
        # Get the processed newsletters from database
        db_manager = daily_processor.content_processor.sqlite_manager
        if db_manager.connect():
            # Get recent newsletters (today)
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%d')
            recent_newsletters = db_manager.get_newsletters_by_date_range(today, today)
            
            if recent_newsletters:
                print(f"📊 Found {len(recent_newsletters)} processed newsletters from today:\n")
                
                for i, newsletter in enumerate(recent_newsletters[-len(test_batch):], 1):  # Show last N processed
                    print(f"📰 Newsletter {i}:")
                    print(f"   📧 From: {newsletter['sender']}")
                    print(f"   📝 Subject: {newsletter['subject']}")
                    print(f"   🏷️  Genre: {newsletter['genre']}")
                    print(f"   📊 Word Count: {newsletter['word_count']}")
                    print(f"   📄 Summary: {newsletter['summary'][:200]}...")
                    print()
            else:
                print("⚠️  No newsletters found in database")
                
            db_manager.disconnect()
        
        # Get final stats
        stats = daily_processor.get_recent_processing_stats()
        print(f"📊 Final Processing Stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Real workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_daily_processor_configuration():
    """Test daily processor configuration without email fetching"""
    print("\n🧪 Testing Daily Processor configuration...")
    
    try:
        # Test without email credentials since we're not fetching emails
        processor = DailyNewsletterProcessor()
        print("✅ DailyNewsletterProcessor initialized")
        
        # Test only the content processor part of configuration
        if processor.content_processor.sqlite_manager.connect():
            processor.content_processor.sqlite_manager.create_tables()
            processor.content_processor.sqlite_manager.disconnect()
            print("✅ Database connection test passed")
            return True
        else:
            print("❌ Database connection test failed")
            return False
            
    except Exception as e:
        print(f"❌ Daily processor configuration test failed: {e}")
        return False

def test_batch_size_validation():
    """Verify that our test creates exactly one batch"""
    print("\n🧪 Testing batch size validation...")
    
    test_newsletters = create_test_newsletters()
    batch_size = BATCH_SIZE
    
    print(f"📊 Test newsletters: {len(test_newsletters)}")
    print(f"📊 Configured batch size: {batch_size}")
    
    if len(test_newsletters) == batch_size:
        print("✅ Perfect! Test newsletters exactly match batch size")
        return True
    elif len(test_newsletters) < batch_size:
        print(f"⚠️  Test newsletters ({len(test_newsletters)}) less than batch size ({batch_size})")
        print("This will still work but won't fully test batch processing")
        return True
    else:
        batches = (len(test_newsletters) + batch_size - 1) // batch_size
        print(f"📊 Test newsletters will create {batches} batches")
        return True

def main():
    """Run complete workflow test: real emails → filtering → 10 newsletters → LLM processing → summaries/genres"""
    print("🧪 Testing Complete Real Workflow: Email Fetching → Processing → Results")
    print("=" * 80)

    # Basic configuration tests
    test_configuration()
    
    if not test_environment_variables():
        print("\n❌ Environment variables not properly configured")
        print("Please set OPENROUTER_API_KEY, EMAIL_ADDRESS, and EMAIL_PASSWORD in your .env file")
        return
    
    # Batch size validation
    test_batch_size_validation()
    
    # Configuration test (no email fetching)
    config_success = test_daily_processor_configuration()
    
    # Main test - complete real workflow
    print("\n" + "=" * 80)
    print("🚀 MAIN TEST: Complete Real Workflow")
    print("🔄 This will: Fetch emails → Filter → Process 10 newsletters → Show summaries/genres")
    print("=" * 80)
    
    # Ask user for confirmation since this makes email and LLM calls
    response = input("\nThis will fetch real emails and make LLM API calls. Continue? (y/N): ")
    if response.lower() != 'y':
        print("⏭️  Skipping workflow test")
        print("\n📋 CONFIGURATION TEST RESULTS:")
        print(f"✅ Configuration: {'PASSED' if config_success else 'FAILED'}")
        return
    
    # Run the main test
    workflow_success = test_real_workflow_with_batch()
    
    # Summary
    print("\n" + "=" * 80)
    print("📋 TEST SUMMARY")
    print("=" * 80)
    
    print(f"✅ Configuration: {'PASSED' if config_success else 'FAILED'}")
    print(f"{'✅' if workflow_success else '❌'} Real Workflow: {'PASSED' if workflow_success else 'FAILED'}")
    
    if config_success and workflow_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("🚀 Complete workflow is working: emails → filtering → processing → results!")
    else:
        print("\n⚠️  Some tests failed - check configuration and try again")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
