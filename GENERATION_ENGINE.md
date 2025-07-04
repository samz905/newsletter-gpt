# Newsletter Generation Engine - Complete Implementation Plan

## Phase 1: Daily Scheduler (Runs at 8 PM Daily)

### 1.1 Daily Email Ingestion
#### Steps:
1. **Connect to IMAP** - Gmail connection with authentication
2. **Fetch daily emails** - Get emails from last 24 hours only
3. **Apply primitive filtering** - Filter for newsletter candidates using unsubscribe detection

#### Unsubscribe Keywords (Only These):
```python
unsubscribe_keywords = [
    'unsubscribe', 'opt out', 'opt-out', 'remove me', 'stop emails',
    'manage preferences', 'email preferences', 'subscription preferences'
]
```

### 1.2 Daily Content Processing

#### 1.2.1 Email to Structured Data Conversion
**Steps:**
1. **LLM Newsletter Identification** - Confirm which emails are actual newsletters based on 1.1
2. **Content Extraction** - Extract clean text from confirmed newsletters
3. **Summary Generation** - Create individual summaries for each newsletter
4. **Genre Classification** - Assign genre tags from approved list
5. **Metadata Enrichment** - Add complete metadata set
6. **Langchain Document Creation** - Create Document objects with text and metadata

#### Genre Tags (Only These):
```python
approved_genres = [
    'Technology',
    'Business',
    'Philosophy',
    'Culture',
    'Science',
    'Health',
    'Productivity',
    'Writing & Creativity',
    'Personal Growth',
    'Finance',
    'Politics',
    'Education',
    'Lifestyle',
    'Humor & Entertainment',
    'Spirituality'
]
```

#### Complete Metadata Set:
```python
metadata = {
    'sender': str,           # Email sender address
    'subject': str,          # Email subject
    'date': str,             # Email date (YYYY-MM-DD format)
    'source': str            # Source link
    'genres': str,            # One of approved_genres
    'word_count': int,       # Summary word count
}
```

#### 1.2.2 SQLite Storage
**Steps:**
1. **Database Connection** - Connect to newsletters.db
2. **Schema Validation** - Ensure tables exist
3. **Langchain Document Storage** - Store Document objects
4. **Index Updates** - Update search indices

#### Database Schema:
```sql
CREATE TABLE newsletters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    sender TEXT NOT NULL,
    subject TEXT NOT NULL,
    summary TEXT NOT NULL,
    source TEXT NOT NULL,
    genre TEXT NOT NULL,
    word_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_newsletters_date ON newsletters(date);
CREATE INDEX idx_newsletters_genre ON newsletters(genre);
CREATE INDEX idx_newsletters_source ON newsletters(source);
```

## Phase 2: Weekly Scheduler (Runs Sunday at 7 AM)

### 2.1 Genre-Based Data Extraction
**Steps:**
1. **Date Range Query** - Get newsletters from last 7 days
2. **Genre Grouping** - Group newsletters by genre tags
3. **Langchain Document Retrieval** - Load Document objects from database

### 2.2 Unified Weekly Digest Generation
**Steps:**
1. **Genre Summary Creation** - Create a unified, comprehensive and non-redundant summary per genre 
2. **Weekly Digest** - Use summaries to create a coherent and engaging weekly digest narrative
3. **Formatting and Output** - Generate final markdown digest
4. **File Creation** - Save digest with timestamp

#### Weekly Digest Structure:
```markdown
# Weekly Newsletter Digest - [DATE]

## Business
[Genre summary with key insights and sources]

## Technology
[Genre summary with key insights and sources]

## Science
[Genre summary with key insights and sources]

[... for each genre present that week]

## Summary Stats
- Total newsletters processed: [NUMBER]
```

## Technical Implementation

### Required Components:
1. **EmailDailyProcessor** - Handles daily email ingestion
2. **SQLiteManager** - Database operations
3. **WeeklyDigestGenerator** - Creates weekly digests

### Langchain Integration:
```python
from langchain.schema import Document

# Create Document object
doc = Document(
    page_content=summary_text,
    metadata={
        'sender': sender_address,
        'subject': email_subject,
        'source': newsletter_source,
        'date': email_date,
        'genre': assigned_genre,
        'word_count': len(summary_text.split()),
    }
)
```

### Scheduler Configuration:
- **Daily Processing**: 8 PM every day
- **Weekly Digest**: Sunday at 7 AM
- **Retry Logic**: 3 attempts with 1-hour intervals
- **Error Handling**: Log failures, continue processing

### File Naming Convention:
- **Daily Logs**: `logs/daily_processing_YYYYMMDD.log`
- **Weekly Digests**: `digests/weekly_digest_YYYYMMDD.md`
- **Database**: `data/newsletters.db`

## Implementation Order:
1. Create SQLite database schema
2. Implement EmailDailyProcessor
3. Set up daily scheduler (8 PM)
4. Implement WeeklyDigestGenerator
5. Set up weekly scheduler (Sunday 7 AM)
6. Add error handling and logging 