import os
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

from email_processing.email_fetcher import EmailFetcher
from processors.email_filters import EmailFilters

load_dotenv()

class EmailDailyProcessor:
    def __init__(self):
        self.email_address = os.getenv("EMAIL_ADDRESS")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        
        if not self.email_address or not self.email_password:
            raise ValueError("EMAIL_ADDRESS and EMAIL_PASSWORD must be set in environment variables")
        
        self.fetcher = EmailFetcher(self.email_address, self.email_password)
        self.filters = EmailFilters()
    
    def process_daily_emails(self) -> List[Dict]:
        print("🚀 Starting daily email processing...")
        print(f"📅 Processing emails from last 24 hours")
        
        # Step 1: Connect to IMAP
        if not self._connect_to_email():
            return []
        
        try:
            # Step 2: Fetch daily emails (last 24 hours only)
            daily_emails = self._fetch_daily_emails()
            if not daily_emails:
                print("📭 No emails found from last 24 hours")
                return []
            
            # Step 3: Apply primitive filtering (unsubscribe detection)
            newsletter_candidates = self._apply_primitive_filtering(daily_emails)
            
            print(f"✅ {len(newsletter_candidates)} newsletter candidates identified")
            return newsletter_candidates
            
        finally:
            # Always disconnect
            self._disconnect_from_email()
    
    def _connect_to_email(self) -> bool:
        """Step 1: Connect to IMAP - Gmail connection with authentication"""
        print("🔐 Connecting to Gmail IMAP server...")
        
        try:
            if self.fetcher.connect():
                print("✅ Successfully connected to Gmail IMAP")
                return True
            else:
                print("❌ Failed to connect to Gmail IMAP")
                return False
        except Exception as e:
            print(f"❌ IMAP connection error: {e}")
            return False
    
    def _fetch_daily_emails(self) -> List[Dict]:
        """Step 2: Fetch daily emails - Get emails from last 24 hours only"""
        print("📧 Fetching emails from last 24 hours...")
        
        try:
            emails = self.fetcher.fetch_emails_from_last_24_hours()
            print(f"📊 Fetched {len(emails)} emails from last 24 hours")
            return emails
        except Exception as e:
            print(f"❌ Error fetching daily emails: {e}")
            return []
    
    def _apply_primitive_filtering(self, emails: List[Dict]) -> List[Dict]:
        """Step 3: Apply primitive filtering - Filter for newsletter candidates using unsubscribe detection"""
        print("🔍 Applying primitive filtering (unsubscribe detection)...")
        
        try:
            filtered_emails = self.filters.apply_primitive_filtering(emails)
            print(f"📊 Primitive filtering results: {len(emails)} → {len(filtered_emails)} newsletter candidates")
            return filtered_emails
        except Exception as e:
            print(f"❌ Error applying primitive filtering: {e}")
            return []
    
    def _disconnect_from_email(self):
        """Disconnect from email server"""
        try:
            self.fetcher.disconnect()
            print("📤 Disconnected from email server")
        except Exception as e:
            print(f"⚠️ Error disconnecting: {e}")

def main():
    """Test the daily email processor"""
    processor = EmailDailyProcessor()
    newsletter_candidates = processor.process_daily_emails()
    
    print(f"\n📋 Summary:")
    print(f"Newsletter candidates found: {len(newsletter_candidates)}")
    
    for i, email in enumerate(newsletter_candidates[:5]):  # Show first 5
        print("First 5 newsletter candidates:")
        print(f"{i+1}. {email.get('subject', 'No Subject')} - {email.get('sender', 'No Sender')}")

if __name__ == "__main__":
    main() 