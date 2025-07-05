from typing import List, Dict, Optional
from datetime import datetime

from processors.email_daily_processor import EmailDailyProcessor
from processors.content_processor import ContentProcessor


class DailyNewsletterProcessor:
    def __init__(self, model: str = None):
        self.daily_processor = EmailDailyProcessor()
        self.content_processor = ContentProcessor(model=model)
    
    def run_daily_processing(self) -> Dict:
        """Execute complete daily newsletter processing workflow"""

        print("🚀 Starting Daily Newsletter Processing")
        print("=" * 60)
        
        start_time = datetime.now()
        results = {
            'success': False,
            'daily_processor_completed': False,
            'content_processor_completed': False,
            'newsletter_candidates_found': 0,
            'newsletters_processed': 0,
            'processing_time': 0,
            'error': None
        }
        
        try:
            # Daily Email Ingestion
            print("\n📧 Daily Email Ingestion")
            newsletter_candidates = self._run_daily_processor()
            
            if newsletter_candidates is None:
                results['error'] = "Daily Email Ingestion failed"
                return results
            
            results['daily_processor_completed'] = True
            results['newsletter_candidates_found'] = len(newsletter_candidates)
            
            if not newsletter_candidates:
                print("📭 No newsletter candidates found - daily processing complete")
                results['success'] = True
                results['processing_time'] = (datetime.now() - start_time).total_seconds()
                return results
            
            # Daily Content Processing
            print("\n🤖 Daily Content Processing")
            content_processor_success = self._run_content_processor(newsletter_candidates)
            
            if not content_processor_success:
                results['error'] = "Daily Content Processing failed"
                return results
            
            results['content_processor_completed'] = True
            results['newsletters_processed'] = len(newsletter_candidates)
            results['success'] = True
            
            # Get final statistics
            stats = self.content_processor.get_processing_stats()
            results['database_stats'] = stats
            
            processing_time = (datetime.now() - start_time).total_seconds()
            results['processing_time'] = processing_time
            
            print(f"\n✅ Daily Newsletter Processing COMPLETED successfully!")
            print(f"📊 Newsletter candidates: {results['newsletter_candidates_found']}")
            print(f"📊 Newsletters processed: {results['newsletters_processed']}")
            print(f"⏱️  Processing time: {processing_time:.2f} seconds")
            
            return results
            
        except Exception as e:
            results['error'] = str(e)
            results['processing_time'] = (datetime.now() - start_time).total_seconds()
            print(f"❌ Daily Newsletter Processing failed: {e}")
            return results
    
    def _run_daily_processor(self) -> Optional[List[Dict]]:
        """Run Daily Email Ingestion"""
        try:
            newsletter_candidates = self.daily_processor.process_daily_emails()
            
            if newsletter_candidates is not None:
                print(f"✅ Daily Email Ingestion completed: {len(newsletter_candidates)} newsletter candidates identified")
                return newsletter_candidates
            else:
                print("❌ Daily Email Ingestion failed")
                return None
                
        except Exception as e:
            print(f"❌ Daily Email Ingestion error: {e}")
            return None
    
    def _run_content_processor(self, newsletter_candidates: List[Dict]) -> bool:
        """Run Daily Content Processing"""
        try:
            success = self.content_processor.process_newsletter_candidates(newsletter_candidates)
            
            if success:
                print(f"✅ Daily Content Processing completed: {len(newsletter_candidates)} newsletters processed and stored")
                return True
            else:
                print("❌ Daily Content Processing failed")
                return False
                
        except Exception as e:
            print(f"❌ Daily Content Processing error: {e}")
            return False
    
    def get_recent_processing_stats(self) -> Dict:
        """Get statistics from recent processing"""
        return self.content_processor.get_processing_stats()
    
    def test_configuration(self) -> bool:
        """Test that all components are properly configured"""
        print("🧪 Testing Daily Newsletter Processor configuration...")
        
        try:
            # Test Daily Email Ingestion configuration
            print("🔧 Testing Daily Email Ingestion configuration...")
            # EmailDailyProcessor will test environment variables in __init__
            
            # Test Daily Content Processing configuration
            print("🔧 Testing Daily Content Processing configuration...")
            # Test database connection
            if self.content_processor.sqlite_manager.connect():
                self.content_processor.sqlite_manager.create_tables()
                self.content_processor.sqlite_manager.disconnect()
                print("✅ Database connection test passed")
            else:
                print("❌ Database connection test failed")
                return False
            
            print("✅ Configuration test completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Configuration test failed: {e}")
            return False


def main():
    """Test the daily newsletter processor"""
    print("🧪 Testing Daily Newsletter Processor")
    print("=" * 60)
    
    try:
        processor = DailyNewsletterProcessor()
        
        # Test configuration first
        if not processor.test_configuration():
            print("❌ Configuration test failed - cannot proceed")
            return
        
        # Run daily processing
        results = processor.run_daily_processing()
        
        print("\n📊 FINAL RESULTS:")
        print("=" * 60)
        print(f"Success: {results['success']}")
        print(f"Daily Email Ingestion Completed: {results['daily_processor_completed']}")
        print(f"Daily Content Processing Completed: {results['content_processor_completed']}")
        print(f"Newsletter Candidates Found: {results['newsletter_candidates_found']}")
        print(f"Newsletters Processed: {results['newsletters_processed']}")
        print(f"Processing Time: {results['processing_time']:.2f} seconds")
        
        if results.get('error'):
            print(f"Error: {results['error']}")
        
        if results.get('database_stats'):
            print(f"Database Stats: {results['database_stats']}")
        
        print("=" * 60)
        
        if results['success']:
            print("✅ Daily Newsletter Processor test PASSED!")
        else:
            print("❌ Daily Newsletter Processor test FAILED!")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 