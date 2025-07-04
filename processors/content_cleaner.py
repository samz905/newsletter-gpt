import re
from typing import List, Dict

class ContentCleaner:
    """Clean and prepare newsletter content for summarization"""
    
    def __init__(self, max_content_length: int = 5000):
        self.max_content_length = max_content_length
    
    def clean_newsletters(self, newsletters: List[Dict]) -> List[Dict]:
        """Clean and prepare newsletter content for summarization"""
        print("🧹 Cleaning newsletter content...")
        
        cleaned_newsletters = []
        
        for newsletter in newsletters:
            cleaned_newsletter = self._clean_single_newsletter(newsletter)
            cleaned_newsletters.append(cleaned_newsletter)
        
        print(f"✅ Cleaned {len(cleaned_newsletters)} newsletters")
        return cleaned_newsletters
    
    def _clean_single_newsletter(self, newsletter: Dict) -> Dict:
        """Clean a single newsletter"""
        body = newsletter.get('body', '')
        
        # Basic cleaning
        cleaned_body = self._apply_basic_cleaning(body)
        
        # Truncate if too long
        if len(cleaned_body) > self.max_content_length:
            cleaned_body = cleaned_body[:self.max_content_length] + "..."
        
        # Create cleaned copy
        cleaned_newsletter = newsletter.copy()
        cleaned_newsletter['cleaned_body'] = cleaned_body
        
        return cleaned_newsletter
    
    def _apply_basic_cleaning(self, body: str) -> str:
        """Apply basic text cleaning"""
        # Replace line breaks with spaces
        cleaned = body.replace('\n', ' ').replace('\r', ' ')
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Remove common email artifacts
        cleaned = re.sub(r'View this email in your browser', '', cleaned)
        cleaned = re.sub(r'If you.*unsubscribe.*', '', cleaned)
        cleaned = re.sub(r'This email was sent to.*', '', cleaned)
        
        return cleaned.strip() 