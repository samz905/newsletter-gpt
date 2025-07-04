from typing import List, Dict
from .imap_connector import ImapConnector
from .email_searcher import EmailSearcher
from .email_parser import EmailParser


class EmailFetcher:
    """Main email fetcher that orchestrates email processing"""
    
    def __init__(self, email_address: str, password: str, 
                 imap_server: str = "imap.gmail.com", port: int = 993):
        self.connector = ImapConnector(email_address, password, imap_server, port)
        self.searcher = None
        self.parser = None
    
    def connect(self) -> bool:
        """Connect to email server"""
        if not self.connector.connect():
            return False
        
        connection = self.connector.get_connection()
        self.searcher = EmailSearcher(connection)
        self.parser = EmailParser(connection)
        return True
    
    def fetch_emails_from_last_7_days(self) -> List[Dict]:
        """Fetch emails from the past 7 days"""
        if not self.searcher or not self.parser:
            print("❌ Email fetcher not properly initialized")
            return []
        
        # Search for emails
        email_ids = self.searcher.search_last_n_days(7)
        if not email_ids:
            return []
        
        # Parse emails (limit to first 50 for performance)
        emails = []
        for email_id in email_ids[:50]:
            parsed_email = self.parser.parse_email(email_id)
            if parsed_email:
                emails.append(parsed_email)
        
        return emails
    
    def disconnect(self):
        """Disconnect from email server"""
        self.connector.disconnect() 