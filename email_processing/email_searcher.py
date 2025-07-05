import imaplib
from datetime import datetime, timedelta
from typing import List, Optional


class EmailSearcher:
    """Search for emails based on criteria"""
    
    def __init__(self, mail_connection: imaplib.IMAP4_SSL):
        self.mail = mail_connection
    
    def search_last_24_hours(self) -> List[bytes]:
        """Search for emails from the last 24 hours (for daily processing)"""
        return self.search_last_n_days(days=1)
    
    def search_last_n_days(self, days: int = 7) -> List[bytes]:
        """Search for emails from the last N days"""
        if not self.mail:
            print("No IMAP connection available")
            return []
        
        try:
            # Select inbox
            self.mail.select("inbox")
            
            # Calculate date N days ago
            n_days_ago = datetime.now() - timedelta(days=days)
            date_string = n_days_ago.strftime("%d-%b-%Y")
            
            # Search for emails from the last N days
            print(f"Searching for emails since {date_string}")
            status, messages = self.mail.search(None, f'SINCE "{date_string}"')
            
            if status != 'OK':
                print("Failed to search emails")
                return []
            
            email_ids = messages[0].split()
            print(f"Found {len(email_ids)} emails from the last {days} days")
            
            return email_ids
            
        except Exception as e:
            print(f"Error searching emails: {e}")
            return [] 