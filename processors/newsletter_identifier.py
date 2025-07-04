import re
from typing import List, Dict
from openai_client import chat_completion

class NewsletterIdentifier:
    """Use LLM to identify which emails are actually newsletters"""
    
    def __init__(self, batch_size: int = 10):
        self.batch_size = batch_size
    
    def identify_newsletters(self, emails: List[Dict]) -> List[Dict]:
        """Use LLM to identify which emails are actually newsletters"""
        print("🤖 Using LLM for newsletter identification...")
        
        newsletter_emails = []
        
        for i in range(0, len(emails), self.batch_size):
            batch = emails[i:i + self.batch_size]
            identified = self._process_batch(batch)
            newsletter_emails.extend(identified)
        
        print(f"✅ LLM identification: {len(emails)} → {len(newsletter_emails)} newsletters")
        return newsletter_emails
    
    def _process_batch(self, batch: List[Dict]) -> List[Dict]:
        """Process a batch of emails for newsletter identification"""
        # Prepare email info for LLM with semantic context
        email_info = []
        for j, email in enumerate(batch):
            semantic_context = self._extract_semantic_context(email['body'])
            email_info.append(f"""
Email {j+1}:
Subject: {email['subject']}
Sender: {email['sender']}
Content Context: {semantic_context}
""")
        
        emails_text = "\n".join(email_info)
        
        prompt = f"""
You are an expert at identifying newsletter emails. Please analyze these emails and determine which ones are newsletters/publications that would be valuable to summarize in a weekly digest.

Look for:
- Regular publications (newsletters, magazines, blogs)
- Educational content
- Industry updates
- Curated content
- Thought leadership pieces

Ignore:
- Promotional emails
- Transactional emails
- Personal emails
- Spam
- One-off announcements

{emails_text}

Please respond with ONLY the numbers of emails that are newsletters (e.g., "1, 3, 5"). If none are newsletters, respond with "None".
"""
        
        try:
            response = chat_completion([{"role": "user", "content": prompt}])
            return self._parse_llm_response(response, batch)
        except Exception as e:
            print(f"❌ LLM identification error: {e}")
            return []
    
    def _extract_semantic_context(self, body: str) -> str:
        """Extract semantic context from first 3 lines of body"""
        if not body:
            return "No content available"
        
        lines = body.split('\n')
        first_three_lines = lines[:3]
        
        # Clean and join the lines
        context_lines = []
        for line in first_three_lines:
            cleaned_line = line.strip()
            if cleaned_line and len(cleaned_line) > 10:  # Skip very short lines
                context_lines.append(cleaned_line)
        
        # Take first 3 meaningful lines, or first 300 chars if few lines
        if len(context_lines) >= 3:
            return " | ".join(context_lines[:3])
        elif context_lines:
            full_context = " | ".join(context_lines)
            if len(full_context) < 200:
                # Add more content if we have very little
                remaining_text = " ".join(lines[len(context_lines):])
                full_context += " | " + remaining_text[:200]
            return full_context[:300]
        else:
            return body[:300] + "..." if len(body) > 300 else body
    
    def _parse_llm_response(self, response: str, batch: List[Dict]) -> List[Dict]:
        """Parse LLM response and return identified newsletters"""
        newsletter_emails = []
        
        if response.strip().lower() == "none":
            return newsletter_emails
        
        # Extract numbers from response
        numbers = re.findall(r'\d+', response)
        
        for num_str in numbers:
            num = int(num_str) - 1  # Convert to 0-based index
            if 0 <= num < len(batch):
                newsletter_emails.append(batch[num])
                print(f"✅ Identified newsletter: {batch[num]['subject'][:50]}...")
        
        return newsletter_emails 