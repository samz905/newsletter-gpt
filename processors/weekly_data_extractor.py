from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import sqlite3

from config import DATABASE_PATH, APPROVED_GENRES
from processors.sqlite_manager import SQLiteManager


class Document:
    """Simple Document class for storing newsletter content and metadata"""
    def __init__(self, page_content: str, metadata: Dict):
        self.page_content = page_content
        self.metadata = metadata


class WeeklyDataExtractor:
    """
    Handles weekly data extraction and grouping:
    - Date Range Query: Get newsletters from last 7 days
    - Genre Grouping: Group newsletters by genre tags
    - Document Retrieval: Load Document objects for digest generation
    """
    
    def __init__(self, db_path: str = None):
        self.sqlite_manager = SQLiteManager(db_path)
        self.approved_genres = APPROVED_GENRES
    
    def extract_weekly_data(self, days_back: int = 7) -> Dict[str, List[Document]]:
        """Extract and group newsletter data from the last N days by genre"""
        print(f"📊 Extracting newsletter data from last {days_back} days...")
        
        try:
            # Step 1: Date Range Query - Get newsletters from last N days
            date_range = self._calculate_date_range(days_back)
            newsletters = self._query_newsletters_by_date_range(date_range)
            
            if not newsletters:
                print(f"⚠️  No newsletters found in the last {days_back} days")
                return {}
            
            print(f"📧 Found {len(newsletters)} newsletters in date range {date_range[0]} to {date_range[1]}")
            
            # Step 2: Genre Grouping - Group newsletters by genre tags
            grouped_data = self._group_newsletters_by_genre(newsletters)
            
            # Step 3: Document Retrieval - Load Document objects from database
            document_groups = self._create_document_groups(grouped_data)
            
            # Summary
            self._print_extraction_summary(document_groups, days_back)
            
            return document_groups
            
        except Exception as e:
            print(f"❌ Weekly data extraction failed: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _calculate_date_range(self, days_back: int) -> Tuple[str, str]:
        """Calculate start and end dates for the query"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        return (
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
    
    def _query_newsletters_by_date_range(self, date_range: Tuple[str, str]) -> List[Dict]:
        """Query newsletters from database within date range"""
        start_date, end_date = date_range
        
        if not self.sqlite_manager.connect():
            print("❌ Failed to connect to database")
            return []
        
        try:
            newsletters = self.sqlite_manager.get_newsletters_by_date_range(start_date, end_date)
            return newsletters
            
        finally:
            self.sqlite_manager.disconnect()
    
    def _group_newsletters_by_genre(self, newsletters: List[Dict]) -> Dict[str, List[Dict]]:
        """Group newsletters by genre tags"""
        print("🏷️  Grouping newsletters by genre...")
        
        grouped = defaultdict(list)
        genre_counts = defaultdict(int)
        
        for newsletter in newsletters:
            genre = newsletter.get('genre', 'Technology')  # Default to Technology if missing
            
            # Validate genre is in approved list
            if genre not in self.approved_genres:
                print(f"⚠️  Invalid genre '{genre}' found, defaulting to 'Technology'")
                genre = 'Technology'
            
            grouped[genre].append(newsletter)
            genre_counts[genre] += 1
        
        # Sort genres by count (most newsletters first)
        sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
        
        print("📊 Genre distribution:")
        for genre, count in sorted_genres:
            print(f"   {genre}: {count} newsletters")
        
        return dict(grouped)
    
    def _create_document_groups(self, grouped_data: Dict[str, List[Dict]]) -> Dict[str, List[Document]]:
        """Create Document objects for each newsletter grouped by genre"""
        print("📄 Creating Document objects...")
        
        document_groups = {}
        total_documents = 0
        
        for genre, newsletters in grouped_data.items():
            documents = []
            
            for newsletter in newsletters:
                # Create Document object with full summary as page_content
                doc = Document(
                    page_content=newsletter.get('summary', ''),
                    metadata={
                        'sender': newsletter.get('sender', ''),
                        'subject': newsletter.get('subject', ''),
                        'date': newsletter.get('date', ''),
                        'genre': newsletter.get('genre', genre),
                        'word_count': newsletter.get('word_count', 0),
                        'id': newsletter.get('id', 0)
                    }
                )
                documents.append(doc)
            
            document_groups[genre] = documents
            total_documents += len(documents)
            print(f"   {genre}: {len(documents)} documents created")
        
        print(f"✅ Created {total_documents} Document objects across {len(document_groups)} genres")
        return document_groups
    
    def _print_extraction_summary(self, document_groups: Dict[str, List[Document]], days_back: int):
        """Print summary of extraction results"""
        print(f"\n📋 Weekly Data Extraction Summary ({days_back} days)")
        print("=" * 60)
        
        total_newsletters = sum(len(docs) for docs in document_groups.values())
        total_words = sum(
            sum(doc.metadata.get('word_count', 0) for doc in docs) 
            for docs in document_groups.values()
        )
        
        print(f"📧 Total newsletters: {total_newsletters}")
        print(f"📝 Total words in summaries: {total_words:,}")
        print(f"🏷️  Genres found: {len(document_groups)}")
        
        if document_groups:
            print(f"\n📊 Genre breakdown:")
            for genre, docs in sorted(document_groups.items(), key=lambda x: len(x[1]), reverse=True):
                word_count = sum(doc.metadata.get('word_count', 0) for doc in docs)
                print(f"   {genre}: {len(docs)} newsletters, {word_count:,} words")
        
        print("=" * 60)
    
    def get_genre_statistics(self, days_back: int = 7) -> Dict:
        """Get detailed statistics for genres in the last N days"""
        print(f"📊 Calculating genre statistics for last {days_back} days...")
        
        try:
            if not self.sqlite_manager.connect():
                return {}
            
            stats = self.sqlite_manager.get_database_stats()
            self.sqlite_manager.disconnect()
            
            return stats
            
        except Exception as e:
            print(f"❌ Failed to get genre statistics: {e}")
            return {}
    
    def get_date_range_summary(self, days_back: int = 7) -> Dict:
        """Get summary of newsletters in date range without full extraction"""
        date_range = self._calculate_date_range(days_back)
        newsletters = self._query_newsletters_by_date_range(date_range)
        
        if not newsletters:
            return {
                'date_range': date_range,
                'total_newsletters': 0,
                'genres': {},
                'date_distribution': {}
            }
        
        # Group by genre
        genre_counts = defaultdict(int)
        date_counts = defaultdict(int)
        
        for newsletter in newsletters:
            genre = newsletter.get('genre', 'Technology')
            date = newsletter.get('date', '')
            
            genre_counts[genre] += 1
            date_counts[date] += 1
        
        return {
            'date_range': date_range,
            'total_newsletters': len(newsletters),
            'genres': dict(genre_counts),
            'date_distribution': dict(date_counts)
        }
    
    def validate_data_quality(self, document_groups: Dict[str, List[Document]]) -> Dict:
        """Validate the quality of extracted data"""
        print("🔍 Validating data quality...")
        
        validation_results = {
            'total_documents': 0,
            'empty_summaries': 0,
            'missing_metadata': 0,
            'invalid_genres': 0,
            'valid_documents': 0,
            'issues': []
        }
        
        for genre, documents in document_groups.items():
            validation_results['total_documents'] += len(documents)
            
            for doc in documents:
                # Check for empty summaries
                if not doc.page_content or len(doc.page_content.strip()) == 0:
                    validation_results['empty_summaries'] += 1
                    validation_results['issues'].append(f"Empty summary in {genre}")
                
                # Check for missing metadata
                required_fields = ['sender', 'subject', 'date', 'genre']
                missing_fields = [field for field in required_fields if not doc.metadata.get(field)]
                if missing_fields:
                    validation_results['missing_metadata'] += 1
                    validation_results['issues'].append(f"Missing metadata {missing_fields} in {genre}")
                
                # Check for invalid genres
                if doc.metadata.get('genre') not in self.approved_genres:
                    validation_results['invalid_genres'] += 1
                    validation_results['issues'].append(f"Invalid genre '{doc.metadata.get('genre')}' in {genre}")
        
        validation_results['valid_documents'] = (
            validation_results['total_documents'] - 
            validation_results['empty_summaries'] - 
            validation_results['missing_metadata'] - 
            validation_results['invalid_genres']
        )
        
        # Print validation summary
        print(f"✅ Validation complete:")
        print(f"   Total documents: {validation_results['total_documents']}")
        print(f"   Valid documents: {validation_results['valid_documents']}")
        print(f"   Issues found: {len(validation_results['issues'])}")
        
        if validation_results['issues']:
            print(f"⚠️  Issues detected:")
            for issue in validation_results['issues'][:5]:  # Show first 5 issues
                print(f"     - {issue}")
            if len(validation_results['issues']) > 5:
                print(f"     - ... and {len(validation_results['issues']) - 5} more")
        
        return validation_results


def main():
    """Test the weekly data extractor"""
    print("🧪 Testing Weekly Data Extractor")
    print("=" * 50)
    
    extractor = WeeklyDataExtractor()
    
    # Test 1: Get date range summary
    print("\n📊 Test 1: Date Range Summary")
    summary = extractor.get_date_range_summary(days_back=7)
    print(f"Date range: {summary['date_range'][0]} to {summary['date_range'][1]}")
    print(f"Total newsletters: {summary['total_newsletters']}")
    print(f"Genres: {summary['genres']}")
    
    # Test 2: Extract weekly data
    print("\n📊 Test 2: Full Weekly Data Extraction")
    document_groups = extractor.extract_weekly_data(days_back=7)
    
    if document_groups:
        # Test 3: Validate data quality
        print("\n🔍 Test 3: Data Quality Validation")
        validation = extractor.validate_data_quality(document_groups)
        
        # Test 4: Show sample documents
        print("\n📄 Test 4: Sample Documents")
        for genre, docs in list(document_groups.items())[:2]:  # Show first 2 genres
            print(f"\n{genre} ({len(docs)} documents):")
            if docs:
                doc = docs[0]  # Show first document
                print(f"   Subject: {doc.metadata.get('subject', '')[:50]}...")
                print(f"   Summary: {doc.page_content[:100]}...")
                print(f"   Metadata: {doc.metadata}")
    
    print("\n✅ Weekly data extractor test complete!")
    print("=" * 50)


if __name__ == "__main__":
    main() 