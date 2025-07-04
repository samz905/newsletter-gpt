from typing import List, Dict

class EmailFilters:
    """Handle primitive email filtering to remove obvious non-newsletters"""
    
    def __init__(self):
        # Only filter out obvious transactional/system emails
        self.skip_keywords = [
            'verification code', 'confirm your', 'reset your password',
            'your account has been', 'account verification', 'please verify',
            'confirm your email', 'activate your account', 'password reset',
            'login attempt', 'security alert', 'suspicious activity',
            'invoice #', 'receipt #', 'payment confirmation',
            'order confirmation', 'shipment', 'delivery notification',
            'transaction completed', 'payment failed', 'card declined'
        ]
        
        # Unsubscribe detection keywords
        self.unsubscribe_keywords = [
            'unsubscribe', 'opt out', 'opt-out', 'remove me', 'stop emails',
            'manage preferences', 'email preferences', 'subscription preferences'
        ]
    
    def apply_primitive_filtering(self, emails: List[Dict]) -> List[Dict]:
        """Apply basic filtering to remove obvious non-newsletters"""
        print("🔍 Applying primitive filtering...")
        
        filtered_emails = []
        
        for i, email in enumerate(emails):
            print(f"Email subject for email {i}: {email.get('subject', 'No Subject')}")
            
            if self._should_keep_email(email):
                filtered_emails.append(email)
                print(f"Email {i} kept")
            else:
                print(f"Email {i} filtered out")
        
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
        
        # Check for unsubscribe links anywhere in the email
        has_unsub = self._has_unsubscribe_option(email)
        if not has_unsub:
            return False
        
        # Only filter out obvious transactional emails by subject or body keywords
        # Be very conservative - let the AI make the real filtering decisions
        for keyword in self.skip_keywords:
            if keyword in subject or keyword in body:
                return False
        
        # Keep everything else - let the AI decide what's a newsletter
        return True
    
    def _has_unsubscribe_option(self, email: Dict) -> bool:
        """Check if email has unsubscribe option anywhere in the email"""
        text_to_check = []
        
        # Check subject
        if email.get('subject'):
            text_to_check.append(email['subject'].lower())
        
        # Check body
        if email.get('body'):
            text_to_check.append(email['body'].lower())
        
        # Check sender
        if email.get('sender'):
            text_to_check.append(email['sender'].lower())
        
        # Check any additional headers or metadata
        if email.get('headers'):
            text_to_check.append(str(email['headers']).lower())
        
        # Combine all text to check
        full_text = ' '.join(text_to_check)
        
        # Look for unsubscribe indicators
        for keyword in self.unsubscribe_keywords:
            if keyword in full_text:
                return True
        
        return False 