# Newsletter Data Preprocessing Strategy

## Overview
Smart two-phase filtering approach that happens weekly - eliminates manual maintenance and optimizes token usage.

Step 1: Primitive Filtering  
Step 2: LLM Subject Filtering  
Step 3: Content Processing

---

## Step 1: Primitive Filtering

### Strategy: Unsubscribe Detection
Goal: Identify potential newsletters using legal compliance indicators

### Detection Signals
- "unsubscribe" (most common)
- "manage preferences" 
- "update email preferences"
- "opt out"
- "remove me"
- "unsubscribe.html" (link patterns)

### Implementation Approach
1. Fetch emails from past 7 days via IMAP
2. Simple text search for unsubscribe indicators
3. Keep filtered newsletters in memory
4. Skip obvious non-newsletters 

---

## Step 2: LLM Subject Filtering

### Strategy: Batch Subject Processing  
Goal: Use LLM to identify real newsletters from subjects only (not full content)

### Filtering Criteria
Include:
- Newsletters (Some are tricky with 'hooks')
- Industry briefings and roundups
- Educational content series

Exclude:
- Promotional emails and sales pitches
- Product updates and changelogs  
- Event invitations
- Personal emails

### Implementation Approach
1. Extract subjects from Phase 1 filtered emails (in memory)
2. Send to LLM with clear filtering prompt
3. Parse response to get confirmed newsletter subjects
4. Send newsletters for the confirmed subjects for content processing 

---

## Step 3: Content Processing 

### Strategy: Clean Confirmed Newsletters Only
Goal: Process only LLM-confirmed newsletters for summarization

### Cleaning Steps
1. HTML tag removal - extract plain text
2. Socials footer removal - clean ending
3. Email header removal - focus on content
4. Whitespace normalization - clean formatting
5. Length validation - ensure sufficient content

### Implementation Approach
- Basic HTML parsing to extract text
- Pattern matching to remove common footers
- Content validation before summarization
- Error handling - skip problematic emails gracefully
- Generate summaries and create weekly digest

---