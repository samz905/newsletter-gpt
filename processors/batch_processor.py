import json
import time
from typing import List, Dict, Optional
from datetime import datetime
import re

from openai_client import chat_completion
from config import (
    DEFAULT_MODEL, BATCH_SIZE, BATCH_INTERVAL, RETRY_ATTEMPTS, 
    RETRY_INTERVAL, APPROVED_GENRES
)


class BatchProcessor:
    """Uses LLM to analyze newsletters and generate summaries."""

    def __init__(self, model: str = None):
        self.model = model or DEFAULT_MODEL
        self.batch_size = BATCH_SIZE
        self.batch_interval = BATCH_INTERVAL
        self.retry_attempts = RETRY_ATTEMPTS
        self.retry_interval = RETRY_INTERVAL
        self.approved_genres = APPROVED_GENRES
    
    def process_newsletter_batches(self, newsletters: List[Dict]) -> List[Dict]:
        """Process newsletters in batches with LLM analysis"""
        
        print(f"🤖 Starting batch processing with {self.model}")
        print(f"📊 Processing {len(newsletters)} newsletters in batches of {self.batch_size}")
        
        processed_newsletters = []
        
        # Process newsletters in batches
        for i in range(0, len(newsletters), self.batch_size):
            batch = newsletters[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (len(newsletters) + self.batch_size - 1) // self.batch_size
            
            print(f"\n📦 Processing batch {batch_num}/{total_batches} ({len(batch)} newsletters)")
            
            # Process batch with retry logic
            batch_results = self._process_single_batch(batch, batch_num)
            
            if batch_results:
                processed_newsletters.extend(batch_results)
                print(f"✅ Batch {batch_num} completed: {len(batch_results)} newsletters processed")
            else:
                print(f"❌ Batch {batch_num} failed after all retries")
            
            # Rate limiting - wait between batches (except for last batch)
            if i + self.batch_size < len(newsletters):
                print(f"⏳ Waiting {self.batch_interval} seconds before next batch...")
                time.sleep(self.batch_interval)
        
        print(f"\n✅ Batch processing complete: {len(processed_newsletters)} newsletters processed")
        return processed_newsletters
    
    def _process_single_batch(self, batch: List[Dict], batch_num: int) -> Optional[List[Dict]]:
        """Process a single batch with retry logic"""
        
        for attempt in range(self.retry_attempts):
            try:
                print(f"🔄 Batch {batch_num}, attempt {attempt + 1}/{self.retry_attempts}")
                
                # Create LLM prompt for batch
                prompt = self._create_batch_prompt(batch)
                
                # Make LLM call
                response = chat_completion([{"role": "user", "content": prompt}], model=self.model)
                
                # Parse structured response
                batch_results = self._parse_batch_response(response, batch)
                
                if batch_results:
                    return batch_results
                else:
                    print(f"⚠️ Batch {batch_num} attempt {attempt + 1} failed: Invalid response format")
                    
            except Exception as e:
                print(f"❌ Batch {batch_num} attempt {attempt + 1} error: {e}")
            
            # Wait before retry (except for last attempt)
            if attempt < self.retry_attempts - 1:
                print(f"⏳ Waiting {self.retry_interval} seconds before retry...")
                time.sleep(self.retry_interval)
        
        return None
    
    def _create_batch_prompt(self, batch: List[Dict]) -> str:
        """Create LLM prompt for batch analysis"""
        
        # Prepare newsletter info for LLM
        newsletter_info = []
        for i, newsletter in enumerate(batch):
            content = newsletter.get('body', '')
            
            newsletter_info.append(f"""
Newsletter {i+1}:
Subject: {newsletter.get('subject', 'No Subject')}
Content: {content}
""")
        
        newsletters_text = "\n".join(newsletter_info)
        approved_genres_text = ", ".join(self.approved_genres)
        
        return f"""
You are an expert newsletter analyst. Analyze these {len(batch)} newsletters and provide structured output.

For each newsletter, provide:
1. A comprehensive summary that captures the main content, key insights, and valuable information. Feel free to format it in markdown format. Ensure the summary comprehensively covers the newsletter content. Don't be afraid of any character limits, just make sure the summary doesn't miss any important information from the newsletter content.
2. A genre classification from the approved list (a single genre for each newsletter)

APPROVED GENRES (use one of these for each): {approved_genres_text}

NEWSLETTERS TO ANALYZE:
{newsletters_text}

RESPOND WITH VALID JSON ONLY (no other text):
{{
    "newsletters": [
    {{
        "newsletter_id": 1,
        "summary": "Comprehensive summary of newsletter content...",
        "genre": "Technology"
    }},
    {{
        "newsletter_id": 2,
        "summary": "Another newsletter summary...",
        "genre": "Business"
    }}
    ]
}}

IMPORTANT: 
- newsletter_id must match the newsletter number (1, 2, 3, etc.)
- genre must be exactly one of the approved genres
- summary should be comprehensive and valuable for a weekly digest
- skip any emails that are not newsletters
- respond with valid JSON only
"""
    
    def _parse_batch_response(self, response: str, batch: List[Dict]) -> Optional[List[Dict]]:
        """Parse LLM batch response and return processed newsletters"""
        
        try:
            # Clean response to extract JSON
            json_match = re.search(r'\{[\s\S]*\}', response)
            if not json_match:
                print("❌ No JSON found in response")
                return None
            
            json_str = json_match.group(0)
            llm_response = json.loads(json_str)
            
            if 'newsletters' not in llm_response:
                print("❌ Invalid response format: missing 'newsletters' key")
                return None
            
            processed_newsletters = []
            
            for newsletter_result in llm_response['newsletters']:
                newsletter_id = newsletter_result.get('newsletter_id', 0)
                summary = newsletter_result.get('summary', '')
                genre = newsletter_result.get('genre', '')
                
                # Validate newsletter_id
                if newsletter_id < 1 or newsletter_id > len(batch):
                    print(f"⚠️ Invalid newsletter_id: {newsletter_id}")
                    continue
                
                # Validate genre
                if genre not in self.approved_genres:
                    print(f"⚠️ Invalid genre '{genre}', defaulting to 'Technology'")
                    genre = 'Technology'
                
                # Get original newsletter (convert to 0-based index)
                original_newsletter = batch[newsletter_id - 1]
                
                # Create processed newsletter
                processed_newsletter = {
                    'original_email': original_newsletter,
                    'summary': summary.strip(),
                    'genre': genre,
                    'sender': original_newsletter.get('sender', ''),
                    'subject': original_newsletter.get('subject', ''),
                    'date': original_newsletter.get('date', ''),
                    'word_count': len(summary.split())
                }
                
                processed_newsletters.append(processed_newsletter)
            
            return processed_newsletters
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            return None
        except Exception as e:
            print(f"❌ Response parsing error: {e}")
            return None


def main():
    """Test the batch processor"""
    # Test with sample newsletters
    test_newsletters = [
        {
            'subject': 'Tech Weekly: AI Breakthroughs',
            'sender': 'tech@example.com',
            'date': '2024-01-15',
            'body': 'This week in AI: OpenAI releases new models, Google announces Gemini updates, and Microsoft integrates AI into Office. The future of work is changing rapidly with these AI advancements.'
        },
        {
            'subject': 'Business Insights: Market Trends',
            'sender': 'business@example.com', 
            'date': '2024-01-15',
            'body': 'Market analysis shows strong growth in tech sector. Key trends include: cloud adoption, remote work tools, and cybersecurity investments. Companies are pivoting to digital-first strategies.'
        }
    ]
    
    processor = BatchProcessor()
    results = processor.process_newsletter_batches(test_newsletters)
    
    print(f"\n📋 Test Results:")
    for i, result in enumerate(results):
        print(f"{i+1}. {result['subject']} -> {result['genre']}")
        print(f"   Summary: {result['summary'][:100]}...")
        print()


if __name__ == "__main__":
    main() 