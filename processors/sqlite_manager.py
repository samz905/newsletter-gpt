import sqlite3
import os
from typing import List, Dict, Optional
from datetime import datetime
from langchain.schema import Document

from config import DATABASE_PATH, DATA_DIR


class SQLiteManager:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DATABASE_PATH
        self.ensure_data_directory()
        self.connection = None
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        data_dir = os.path.dirname(self.db_path)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            print(f"📁 Created data directory: {data_dir}")
    
    def connect(self) -> bool:
        """Connect to SQLite database"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable dict-like access
            print(f"🔗 Connected to database: {self.db_path}")
            return True
        except sqlite3.Error as e:
            print(f"❌ Database connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from database"""
        if self.connection:
            self.connection.close()
            self.connection = None
            print("📤 Disconnected from database")
    
    def create_tables(self) -> bool:
        """Create database tables and indices"""
        if not self.connection:
            print("❌ No database connection")
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # Create newsletters table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS newsletters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    sender TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    genre TEXT NOT NULL,
                    word_count INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indices for efficient queries
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_newsletters_date ON newsletters(date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_newsletters_genre ON newsletters(genre)")
            
            self.connection.commit()
            print("✅ Database tables and indices created successfully")
            return True
            
        except sqlite3.Error as e:
            print(f"❌ Error creating tables: {e}")
            return False
    
    def store_processed_newsletters(self, processed_newsletters: List[Dict]) -> bool:
        """Store processed newsletters as Langchain Documents"""
        
        if not self.connection:
            print("❌ No database connection")
            return False
        
        if not processed_newsletters:
            print("📭 No newsletters to store")
            return True
        
        try:
            cursor = self.connection.cursor()
            
            # Prepare data for insertion
            newsletter_data = []
            for newsletter in processed_newsletters:
                # Convert to proper date format
                date_str = self._normalize_date(newsletter.get('date', ''))
                
                newsletter_data.append((
                    date_str,
                    newsletter.get('sender', ''),
                    newsletter.get('subject', ''),
                    newsletter.get('summary', ''),
                    newsletter.get('genre', ''),
                    newsletter.get('word_count', 0)
                ))
            
            # Insert newsletters
            cursor.executemany("""
                INSERT INTO newsletters (date, sender, subject, summary, genre, word_count)
                VALUES (?, ?, ?, ?, ?, ?)
            """, newsletter_data)
            
            self.connection.commit()
            print(f"✅ Stored {len(processed_newsletters)} newsletters in database")
            return True
            
        except sqlite3.Error as e:
            print(f"❌ Error storing newsletters: {e}")
            return False
    
    def create_documents(self, processed_newsletters: List[Dict]) -> List[Document]:
        """Create Document objects from processed newsletters"""    
        documents = []
        
        for newsletter in processed_newsletters:
            # Create Document with summary as page_content and metadata
            doc = Document(
                page_content=newsletter.get('summary', ''),
                metadata={
                    'sender': newsletter.get('sender', ''),
                    'subject': newsletter.get('subject', ''),
                    'date': newsletter.get('date', ''),
                    'genre': newsletter.get('genre', ''),
                    'word_count': newsletter.get('word_count', 0),
                }
            )
            documents.append(doc)
        
        print(f"📄 Created {len(documents)} Langchain Documents")
        return documents
    
    def get_newsletters_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """Get newsletters within date range"""
        if not self.connection:
            print("❌ No database connection")
            return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM newsletters 
                WHERE date BETWEEN ? AND ?
                ORDER BY date DESC
            """, (start_date, end_date))
            
            rows = cursor.fetchall()
            newsletters = [dict(row) for row in rows]
            
            print(f"📊 Retrieved {len(newsletters)} newsletters from {start_date} to {end_date}")
            return newsletters
            
        except sqlite3.Error as e:
            print(f"❌ Error retrieving newsletters: {e}")
            return []
    
    def get_newsletters_by_genre(self, genre: str, days: int = 7) -> List[Dict]:
        """Get newsletters by genre from last N days"""
        if not self.connection:
            print("❌ No database connection")
            return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM newsletters 
                WHERE genre = ? AND date >= date('now', '-{} days')
                ORDER BY date DESC
            """.format(days), (genre,))
            
            rows = cursor.fetchall()
            newsletters = [dict(row) for row in rows]
            
            print(f"📊 Retrieved {len(newsletters)} {genre} newsletters from last {days} days")
            return newsletters
            
        except sqlite3.Error as e:
            print(f"❌ Error retrieving newsletters by genre: {e}")
            return []
    
    def get_all_genres_from_last_week(self) -> List[str]:
        """Get all genres that have newsletters from last 7 days"""
        if not self.connection:
            print("❌ No database connection")
            return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT DISTINCT genre FROM newsletters 
                WHERE date >= date('now', '-7 days')
                ORDER BY genre
            """)
            
            rows = cursor.fetchall()
            genres = [row[0] for row in rows]
            
            print(f"📊 Found {len(genres)} genres from last week: {genres}")
            return genres
            
        except sqlite3.Error as e:
            print(f"❌ Error retrieving genres: {e}")
            return []
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        if not self.connection:
            print("❌ No database connection")
            return {}
        
        try:
            cursor = self.connection.cursor()
            
            # Total newsletters
            cursor.execute("SELECT COUNT(*) FROM newsletters")
            total_newsletters = cursor.fetchone()[0]
            
            # Newsletters by genre
            cursor.execute("""
                SELECT genre, COUNT(*) as count 
                FROM newsletters 
                GROUP BY genre 
                ORDER BY count DESC
            """)
            genre_stats = dict(cursor.fetchall())
            
            # Recent newsletters (last 7 days)
            cursor.execute("""
                SELECT COUNT(*) FROM newsletters 
                WHERE date >= date('now', '-7 days')
            """)
            recent_newsletters = cursor.fetchone()[0]
            
            stats = {
                'total_newsletters': total_newsletters,
                'recent_newsletters': recent_newsletters,
                'genre_stats': genre_stats
            }
            
            print(f"📊 Database stats: {stats}")
            return stats
            
        except sqlite3.Error as e:
            print(f"❌ Error getting database stats: {e}")
            return {}
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string to YYYY-MM-DD format"""
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d')
        
        # Try to parse various date formats
        try:
            # If it's already in YYYY-MM-DD format
            if len(date_str) == 10 and date_str.count('-') == 2:
                return date_str
            
            # Try to parse email date format
            from email.utils import parsedate_to_datetime
            parsed_date = parsedate_to_datetime(date_str)
            return parsed_date.strftime('%Y-%m-%d')
            
        except Exception:
            # Default to current date
            return datetime.now().strftime('%Y-%m-%d')


def main():
    """Test the SQLite manager"""
    manager = SQLiteManager()
    
    # Test connection and table creation
    if manager.connect():
        manager.create_tables()
        
        # Test data
        test_newsletters = [
            {
                'sender': 'tech@example.com',
                'subject': 'Tech Weekly: AI Breakthroughs',
                'summary': 'This week in AI: OpenAI releases new models, Google announces Gemini updates.',
                'date': '2024-01-15',
                'genre': 'Technology',
                'word_count': 15
            },
            {
                'sender': 'business@example.com',
                'subject': 'Business Insights: Market Trends',
                'summary': 'Market analysis shows strong growth in tech sector.',
                'date': '2024-01-15',
                'genre': 'Business',
                'word_count': 10
            }
        ]
        
        # Test storing newsletters
        manager.store_processed_newsletters(test_newsletters)
        
        # Test creating Langchain documents
        documents = manager.create_documents(test_newsletters)
        
        # Test retrieving data
        manager.get_database_stats()
        
        manager.disconnect()
    
    print("✅ SQLite Manager test completed")


if __name__ == "__main__":
    main() 