# Configuration file for Newsletter Generation Engine

# Model Configuration - Single source of truth for model switching
DEFAULT_MODEL = "google/gemini-2.0-flash-exp:free"

# Alternative models (uncomment to switch)
# DEFAULT_MODEL = "gpt-3.5-turbo"
# DEFAULT_MODEL = "gpt-4-0613"
# DEFAULT_MODEL = "anthropic/claude-3-sonnet:beta"

# Batch Processing Configuration
BATCH_SIZE = 10  # newsletters in the prompt per LLM call
BATCH_INTERVAL = 3600  # 1 hour between batches (seconds)
RETRY_ATTEMPTS = 3  # retries per failed call
RETRY_INTERVAL = 600  # 10 minutes between retries (seconds)

# Unsubscribe Keywords (Only These - from Generation Engine spec)
UNSUBSCRIBE_KEYWORDS = [
    'unsubscribe', 'opt out', 'opt-out', 'remove me', 'stop emails',
    'manage preferences', 'email preferences', 'subscription preferences'
]

# Genre Tags (Only These - from Generation Engine spec)
APPROVED_GENRES = [
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

# Database Configuration
DATABASE_PATH = "data/newsletters.db"

# Scheduler Configuration
DAILY_PROCESSING_TIME = "20:00"  # 8 PM daily
WEEKLY_DIGEST_TIME = "07:00"     # Sunday 7 AM

# File Paths
LOG_DIR = "logs"
DIGEST_DIR = "digests"
DATA_DIR = "data" 