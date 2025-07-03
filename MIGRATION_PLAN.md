# Newsletter GPT Migration Plan

## Overview
Transform the current newsletter app from Zapier-based immediate processing to a sophisticated daily batch system with enhanced RAG and OpenRouter integration.

**Current State:** Email → Zapier → Immediate AI Processing → Notion  
**Target State:** Email Collection → Daily Batch Processing → Enhanced Summaries → Notion

---

## Phase 1: Foundation Setup

### Task 1.1: OpenRouter Integration
**Goal:** Replace OpenAI with OpenRouter's free DeepSeek model

- [ ] Install/update OpenAI client library
- [ ] Create new `config/settings.py` with OpenRouter configuration
- [ ] Update environment variables (add `OPENROUTER_API_KEY`)
- [ ] Create wrapper function for OpenRouter client
- [ ] Test basic chat completion with DeepSeek model
- [ ] Update existing OpenAI calls to use new client

**Test:** Simple chat completion request returns valid response

```bash
# Test command
python -c "from config.settings import get_openrouter_client; print(get_openrouter_client().chat.completions.create(model='deepseek/deepseek-chat-v3-0324:free', messages=[{'role': 'user', 'content': 'Hello'}]).choices[0].message.content)"
```

### Task 1.2: Database Setup
**Goal:** Create local storage for newsletter collection

- [ ] Install SQLite dependencies
- [ ] Create `models/database.py` with SQLAlchemy models
- [ ] Define Newsletter table schema (id, sender, subject, content, received_date, processed, summary)
- [ ] Create database initialization function
- [ ] Add basic CRUD operations
- [ ] Create database migration script

**Test:** Create, read, update, delete newsletter records

```bash
# Test command
python -c "from models.database import create_newsletter, get_newsletter; id = create_newsletter('test@example.com', 'Test Subject', 'Test content'); print(get_newsletter(id))"
```

### Task 1.3: Basic Email Collection
**Goal:** Replace Zapier with IMAP email collection

- [ ] Install `imaplib` and email parsing dependencies
- [ ] Create `email_collector.py` with IMAP connection
- [ ] Implement basic email fetching (last 24 hours)
- [ ] Add email filtering (sender whitelist, subject keywords)
- [ ] Store fetched emails in database
- [ ] Handle duplicate prevention

**Test:** Fetch emails from configured inbox and store in database

```bash
# Test command
python email_collector.py --dry-run
```

---

## Phase 2: Processing Pipeline

### Task 2.1: Text Processing Utilities
**Goal:** Improve content preprocessing before summarization

- [ ] Create `utils/text_processor.py`
- [ ] Implement HTML cleaning function
- [ ] Add email signature removal
- [ ] Create newsletter structure detection
- [ ] Add content validation (minimum length, etc.)

**Test:** Process raw email content and verify cleaned output

```bash
# Test command
python -c "from utils.text_processor import clean_email_content; print(clean_email_content('<html><body>Test newsletter content</body></html>'))"
```

### Task 2.2: Enhanced Chunking
**Goal:** Replace fixed-size chunks with semantic chunking

- [ ] Install sentence-transformers library
- [ ] Create `rag_pipeline.py` with semantic chunking
- [ ] Implement smart text splitting (by paragraphs, sections)
- [ ] Add chunk metadata (position, topic hints)
- [ ] Test with various newsletter formats

**Test:** Chunk sample newsletter and verify logical boundaries

```bash
# Test command
python -c "from rag_pipeline import semantic_chunk; chunks = semantic_chunk('Sample long newsletter content...'); print(f'Created {len(chunks)} chunks')"
```

### Task 2.3: Vector Storage
**Goal:** Add embedding-based content storage

- [ ] Install ChromaDB
- [ ] Setup local vector database
- [ ] Create embedding generation functions
- [ ] Implement document storage with metadata
- [ ] Add similarity search functionality

**Test:** Store and retrieve documents by similarity

```bash
# Test command
python -c "from rag_pipeline import store_document, search_similar; store_document('test content'); results = search_similar('test query'); print(len(results))"
```

### Task 2.4: Individual Newsletter Processing
**Goal:** Update single newsletter summarization with new pipeline

- [ ] Create `newsletter_processor.py`
- [ ] Integrate text cleaning, chunking, and embedding
- [ ] Update summarization with better prompts for DeepSeek
- [ ] Add error handling and retry logic
- [ ] Test with various newsletter types

**Test:** Process a single newsletter end-to-end

```bash
# Test command
python newsletter_processor.py --newsletter-id 1
```

---

## Phase 3: Daily Batch System

### Task 3.1: Batch Processing Engine
**Goal:** Create daily newsletter aggregation and processing

- [ ] Create `daily_processor.py`
- [ ] Implement newsletter grouping by date
- [ ] Add batch processing for multiple newsletters
- [ ] Create daily summary generation logic
- [ ] Add progress tracking and logging

**Test:** Process all newsletters from a specific date

```bash
# Test command
python daily_processor.py --date 2024-01-15 --dry-run
```

### Task 3.2: Enhanced Daily Summaries
**Goal:** Create comprehensive daily digest format

- [ ] Design daily summary template
- [ ] Implement topic grouping across newsletters
- [ ] Add section headers (Tech News, Business, etc.)
- [ ] Include newsletter source attribution
- [ ] Add reading time estimates

**Test:** Generate formatted daily summary

```bash
# Test command
python daily_processor.py --date 2024-01-15 --format-only
```

### Task 3.3: Scheduling System
**Goal:** Automate email collection and daily processing

- [ ] Install APScheduler
- [ ] Create `scheduler.py` with job definitions
- [ ] Add email collection job (every 30 minutes)
- [ ] Add daily processing job (8 PM)
- [ ] Implement logging and error handling
- [ ] Add graceful shutdown

**Test:** Run scheduler for 1 hour and verify job execution

```bash
# Test command
python scheduler.py --test-mode --duration 3600
```

---

## Phase 4: Integration & Enhancement

### Task 4.1: Updated Notion Integration
**Goal:** Enhance Notion pages with daily summaries

- [ ] Update `notion_client.py` for daily summary format
- [ ] Add rich text formatting for sections
- [ ] Include newsletter source links
- [ ] Add tags/categories for topics
- [ ] Implement error handling for API limits

**Test:** Create a test daily summary page in Notion

```bash
# Test command
python notion_client.py --test-summary
```

### Task 4.2: FastAPI Control Panel
**Goal:** Create simple monitoring and control interface

- [ ] Update `main.py` with new endpoints
- [ ] Add health check endpoint
- [ ] Create manual trigger endpoints
- [ ] Add basic status dashboard (optional HTML page)
- [ ] Include system metrics

**Test:** Start server and verify all endpoints respond

```bash
# Test command
uvicorn main:app --reload &
curl localhost:8000/health
```

### Task 4.3: Configuration Management
**Goal:** Centralize and improve configuration

- [ ] Create comprehensive `config/settings.py`
- [ ] Add environment variable validation
- [ ] Include email server settings
- [ ] Add processing schedule configuration
- [ ] Create settings validation

**Test:** Load and validate all configuration

```bash
# Test command
python -c "from config.settings import validate_config; validate_config()"
```

---

## Phase 5: Testing & Deployment

### Task 5.1: End-to-End Testing
**Goal:** Verify complete system functionality

- [ ] Create test newsletter samples
- [ ] Test email collection → processing → Notion flow
- [ ] Verify daily summary generation
- [ ] Test error handling scenarios
- [ ] Performance testing with multiple newsletters

**Test:** Complete daily workflow simulation

```bash
# Test command
python test_full_workflow.py --simulate-day
```

### Task 5.2: Documentation & Cleanup
**Goal:** Finalize deployment-ready system

- [ ] Update README.md with new setup instructions
- [ ] Create example configuration files
- [ ] Add troubleshooting guide
- [ ] Remove old Zapier-related code
- [ ] Update requirements.txt

**Test:** Fresh installation following README instructions

### Task 5.3: Migration Script
**Goal:** Smooth transition from old system

- [ ] Create migration script for existing data
- [ ] Backup current Notion pages
- [ ] Test rollback procedures
- [ ] Create deployment checklist

**Test:** Run migration on copy of production data

---

## Quick Start Commands

```bash
# Phase 1
pip install -r requirements.txt
python setup_database.py
python test_openrouter.py

# Phase 2  
python email_collector.py --setup
python test_rag_pipeline.py

# Phase 3
python daily_processor.py --setup
python scheduler.py --install

# Phase 4
python test_notion_integration.py
uvicorn main:app --reload

# Phase 5
python test_full_workflow.py
```

## Success Criteria

- ✅ Zero dependency on Zapier
- ✅ Daily summaries instead of individual processing
- ✅ Free DeepSeek model working
- ✅ Enhanced RAG providing better summaries
- ✅ Automated email collection and processing
- ✅ Reliable Notion integration
- ✅ Simple monitoring and control interface

## Rollback Plan

If any phase fails:
1. Keep current system running during migration
2. Test each phase thoroughly before proceeding
3. Maintain database backups
4. Document known issues and workarounds
5. Have old Zapier integration ready to re-enable 