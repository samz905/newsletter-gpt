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
1. **Content Extraction** - Extract clean text from confirmed newsletters
2. **Batch Processing** - Use 10 newsletters in the prompt for LLM processing
3. **LLM Batch Analysis** - Single call for 10 newsletters returning structured output (summary + genre for each)
4. **Data Extraction** - Extract individual newsletter data from structured LLM response
5. **Local Metadata Enrichment** - Add metadata properties (no LLM needed)
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

#### Batch Processing & Rate Limiting:
```python
# Batch Configuration
BATCH_SIZE = 10  # newsletters in the prompt per LLM call
BATCH_INTERVAL = 3600  # 1 hour between batches (seconds)
RETRY_ATTEMPTS = 3  # retries per failed call
RETRY_INTERVAL = 600  # 10 minutes between retries (seconds)
```

#### LLM Structured Output Format:
```json
{
  "newsletters": [
    {
      "newsletter_id": 1,
      "summary": "Comprehensive summary of newsletter content...",
      "genre": "Technology"
    },
    {
      "newsletter_id": 2, 
      "summary": "Another newsletter summary...",
      "genre": "Business"
    }
    // ... up to 10 newsletters per batch
  ]
}
```

#### Local Metadata Enrichment (No LLM Required):
```python
# Extracted directly from email properties
metadata = {
    'sender': email.sender,           # Email sender address  
    'subject': email.subject,         # Email subject
    'date': email.date,              # Email date (YYYY-MM-DD format)
    'genre': llm_response.genre,     # From LLM batch response
    'word_count': len(llm_response.summary.split()),  # From LLM summary
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
    genre TEXT NOT NULL,
    word_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_newsletters_date ON newsletters(date);
CREATE INDEX idx_newsletters_genre ON newsletters(genre);
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
[Genre summary with key insights]

## Technology
[Genre summary with key insights]

## Science
[Genre summary with key insights]

[... for each genre present that week]

## Summary Stats
- Total newsletters processed: [NUMBER]
```

## Technical Implementation

### Required Components:
1. **EmailDailyProcessor** - Handles daily email ingestion and batch processing
2. **BatchProcessor** - Manages batching, rate limiting, and LLM calls  
3. **SQLiteManager** - Database operations
4. **WeeklyDigestGenerator** - Creates weekly digests

### Langchain Integration:
```python
from langchain.schema import Document

# Process batch response and create Document objects
for newsletter_result in llm_batch_response['newsletters']:
    doc = Document(
        page_content=newsletter_result['summary'],
        metadata={
            'sender': original_email.sender,
            'subject': original_email.subject,
            'date': original_email.date,
            'genre': newsletter_result['genre'],
            'word_count': len(newsletter_result['summary'].split()),
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
2. Implement BatchProcessor with rate limiting and retry logic
3. Implement EmailDailyProcessor with batch integration
4. Set up daily scheduler (8 PM) 
5. Implement WeeklyDigestGenerator
6. Set up weekly scheduler (Sunday 7 AM)
7. Add comprehensive error handling and logging 