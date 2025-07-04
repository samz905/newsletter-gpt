from typing import List, Dict

class EmailFilters:
    """Handle primitive email filtering to remove obvious non-newsletters"""
    
    def __init__(self):
        self.skip_keywords = [
            'verify', 'confirmation', 'receipt', 'invoice', 'payment',
            'password', 'security', 'login', 'account', 'support',
            'delivery', 'shipping', 'order', 'transaction'
        ]
        
        self.newsletter_domains = [
            'substack.com', 'convertkit.com', 'mailchimp.com', 
            'beehiiv.com', 'ghost.io'
        ]
    
    def apply_primitive_filtering(self, emails: List[Dict]) -> List[Dict]:
        """Apply basic filtering to remove obvious non-newsletters"""
        print("🔍 Applying primitive filtering...")
        
        filtered_emails = []
        
        for email in emails:
            if self._should_keep_email(email):
                filtered_emails.append(email)
        
        print(f"✅ Primitive filtering: {len(emails)} → {len(filtered_emails)} emails")
        return filtered_emails
    
    def _should_keep_email(self, email: Dict) -> bool:
        """Check if email should be kept after primitive filtering"""
        # Skip if missing essential fields
        if not email.get('subject') or not email.get('sender'):
            return False
        
        subject = email['subject'].lower()
        sender = email['sender'].lower()
        body = email.get('body', '').lower()
        
        # Skip if subject contains obvious non-newsletter keywords
        if any(keyword in subject for keyword in self.skip_keywords):
            return False
            
        # Check for newsletter indicators
        has_unsubscribe = any(indicator in body for indicator in ['unsubscribe', 'opt-out', 'manage preferences'])
        has_newsletter_domain = any(domain in sender for domain in self.newsletter_domains)
        
        # Keep if has unsubscribe link OR is from known newsletter domain
        return has_unsubscribe or has_newsletter_domain 