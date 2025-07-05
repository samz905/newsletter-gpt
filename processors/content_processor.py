from typing import List, Dict, Optional
from datetime import datetime

from processors.content_cleaner import ContentCleaner
from processors.batch_processor import BatchProcessor
from processors.sqlite_manager import SQLiteManager


class ContentProcessor:
    def __init__(self, model: str = None):
        self.content_cleaner = ContentCleaner(max_content_length=3000)
        self.batch_processor = BatchProcessor(model=model)
        self.sqlite_manager = SQLiteManager()
    
    def process_newsletter_candidates(self, newsletter_candidates: List[Dict]) -> bool:
        """Convert newsletter candidates to structured data"""
        
        print("🚀 Starting Content Processing")
        print(f"📊 Processing {len(newsletter_candidates)} newsletter candidates")
        
        if not newsletter_candidates:
            print("📭 No newsletter candidates to process")
            return True
        
        try:
            # Step 1: Content Extraction - Extract clean text
            cleaned_newsletters = self._extract_clean_content(newsletter_candidates)
            if not cleaned_newsletters:
                print("❌ No newsletters after content extraction")
                return False
            
            # Step 2: Batch Processing - LLM analysis (10 newsletters per call)
            processed_newsletters = self._batch_process_newsletters(cleaned_newsletters)
            if not processed_newsletters:
                print("❌ No newsletters after batch processing")
                return False
            
            # Step 3: Local Metadata Enrichment - Add metadata properties
            enriched_newsletters = self._enrich_metadata(processed_newsletters)
            
            # Step 4: Langchain Document Creation - Create Document objects
            self._create_documents(enriched_newsletters)
            
            # Step 5: SQLite Storage - Store processed newsletters
            success = self._store_newsletters(enriched_newsletters)
            
            if success:
                print(f"✅ Content processing completed successfully: {len(enriched_newsletters)} newsletters processed and stored")
                return True
            else:
                print("❌ Content processing failed during storage")
                return False
                
        except Exception as e:
            print(f"❌ Content processing error: {e}")
            return False
    
    def _extract_clean_content(self, newsletter_candidates: List[Dict]) -> List[Dict]:
        """
        Step 1: Content Extraction - Extract clean text from newsletter candidates
        """
        print("🧹 Step 1: Content Extraction - Cleaning newsletter content")
        
        try:
            cleaned_newsletters = self.content_cleaner.clean_newsletters(newsletter_candidates)
            print(f"✅ Content extraction completed: {len(cleaned_newsletters)} newsletters cleaned")
            return cleaned_newsletters
        except Exception as e:
            print(f"❌ Content extraction error: {e}")
            return []
    
    def _batch_process_newsletters(self, cleaned_newsletters: List[Dict]) -> List[Dict]:
        """
        Step 2: Batch Processing - Use BatchProcessor for LLM analysis
        """
        print("🤖 Step 2: Batch Processing - LLM analysis with rate limiting")
        
        try:
            processed_newsletters = self.batch_processor.process_newsletter_batches(cleaned_newsletters)
            print(f"✅ Batch processing completed: {len(processed_newsletters)} newsletters processed")
            return processed_newsletters
        except Exception as e:
            print(f"❌ Batch processing error: {e}")
            return []
    
    def _enrich_metadata(self, processed_newsletters: List[Dict]) -> List[Dict]:
        """
        Step 3: Local Metadata Enrichment - Add metadata properties (no LLM needed)
        """
        print("📊 Step 3: Local Metadata Enrichment - Adding metadata properties")
        
        enriched_newsletters = []
        
        for newsletter in processed_newsletters:
            # Enrich with additional metadata
            enriched_newsletter = newsletter.copy()
            
            # Add processing timestamp
            enriched_newsletter['processed_at'] = datetime.now().isoformat()
            
            # Normalize date format
            enriched_newsletter['date'] = self._normalize_date(newsletter.get('date', ''))
            
            # Ensure all required fields are present
            enriched_newsletter['sender'] = newsletter.get('sender', '')
            enriched_newsletter['subject'] = newsletter.get('subject', '')
            enriched_newsletter['summary'] = newsletter.get('summary', '')
            enriched_newsletter['genre'] = newsletter.get('genre', 'Technology')
            enriched_newsletter['word_count'] = newsletter.get('word_count', 0)
            
            enriched_newsletters.append(enriched_newsletter)
        
        print(f"✅ Metadata enrichment completed: {len(enriched_newsletters)} newsletters enriched")
        return enriched_newsletters
    
    def _create_documents(self, enriched_newsletters: List[Dict]) -> List:
        """
        Step 4: Langchain Document Creation - Create Document objects with text and metadata
        """
        print("📄 Step 4: Langchain Document Creation - Creating Document objects")
        
        try:
            documents = self.sqlite_manager.create_documents(enriched_newsletters)
            print(f"✅ Langchain document creation completed: {len(documents)} documents created")
            return documents
        except Exception as e:
            print(f"❌ Document creation error: {e}")
            return []
    
    def _store_newsletters(self, enriched_newsletters: List[Dict]) -> bool:
        """
        Step 5: SQLite Storage - Store processed newsletters in database
        """
        print("💾 Step 5: SQLite Storage - Storing processed newsletters")
        
        try:
            # Connect to database
            if not self.sqlite_manager.connect():
                return False
            
            # Create tables if they don't exist
            if not self.sqlite_manager.create_tables():
                return False
            
            # Store newsletters
            success = self.sqlite_manager.store_processed_newsletters(enriched_newsletters)
            
            # Disconnect
            self.sqlite_manager.disconnect()
            
            if success:
                print(f"✅ SQLite storage completed: {len(enriched_newsletters)} newsletters stored")
                return True
            else:
                print("❌ SQLite storage failed")
                return False
                
        except Exception as e:
            print(f"❌ Storage error: {e}")
            self.sqlite_manager.disconnect()
            return False
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string to YYYY-MM-DD format"""
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d')
        
        try:
            # Try to parse various date formats
            from email.utils import parsedate_to_datetime
            parsed_date = parsedate_to_datetime(date_str)
            return parsed_date.strftime('%Y-%m-%d')
        except Exception:
            # Default to current date
            return datetime.now().strftime('%Y-%m-%d')
    
    def get_processing_stats(self) -> Dict:
        """Get processing statistics from database"""
        try:
            if self.sqlite_manager.connect():
                stats = self.sqlite_manager.get_database_stats()
                self.sqlite_manager.disconnect()
                return stats
            return {}
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {}


def main():
    """Test the content processor"""
    # Test with sample newsletter candidates
    test_candidates = [
        {
            'id': '1',
            'subject': 'Tech Weekly: AI Breakthroughs',
            'sender': 'tech@example.com',
            'date': 'Mon, 15 Jan 2024 10:00:00 +0000',
            'body': 'This week in AI: OpenAI releases new models, Google announces Gemini updates, and Microsoft integrates AI into Office. The future of work is changing rapidly with these AI advancements. Key developments include improved language models, better reasoning capabilities, and more efficient training methods.'
        },
        {
            'id': '2',
            'subject': 'Business Insights: Market Trends',
            'sender': 'business@example.com',
            'date': 'Mon, 15 Jan 2024 11:00:00 +0000',
            'body': 'Market analysis shows strong growth in tech sector. Key trends include: cloud adoption, remote work tools, and cybersecurity investments. Companies are pivoting to digital-first strategies. The quarterly earnings show consistent growth across major tech companies.'
        }
    ]
    
    processor = ContentProcessor()
    
    print("🧪 Testing Content Processing")
    print("=" * 50)
    
    # Test the complete workflow
    success = processor.process_newsletter_candidates(test_candidates)
    
    if success:
        # Get processing stats
        stats = processor.get_processing_stats()
        print(f"\n📊 Processing Stats: {stats}")
        
        print("\n✅ Content processing test completed successfully!")
    else:
        print("\n❌ Content processing test failed!")
    
    print("=" * 50)


if __name__ == "__main__":
    main() 