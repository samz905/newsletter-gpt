The new pipeline for going from emails -> weekly digest

1. Daily scheduler - Runs at a fixed time each day - takes all the emails received that day and:
   
1.1. First we filter for 'likely' newsletter content using:
unsubscribe_keywords = [
    'unsubscribe', 'opt out', 'opt-out', 'remove me', 'stop emails',
    'manage preferences', 'email preferences', 'subscription preferences'
]

1.2 Then we:
1.2.1 Summarize them, add genre tags and any other useful metadata -> email to structured data
1.2.2 Store the structured data to SQLite


2. Weekly scheduler 

2.1 Extracts summaries for each genre - maybe use semantic chunking here since a lot of content could come for one genre
2.2. Create a unified summary that is comprehensive and non-redundant