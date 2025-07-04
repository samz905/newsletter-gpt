import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from email_processing.email_fetcher import EmailFetcher
from dotenv import load_dotenv
import argparse

load_dotenv()


def test_email_fetcher():
    """Test function for modular email fetcher"""
    # Try to get credentials from environment
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")
    
    if not email_address or not email_password:
        print("❌ Email credentials not found in environment variables")
        print("Please set EMAIL_ADDRESS and EMAIL_PASSWORD in your .env file")
        return False
    
    fetcher = EmailFetcher(email_address, email_password)
    
    if not fetcher.connect():
        return False
    
    try:
        emails = fetcher.fetch_emails_from_last_7_days()
        print(f"✅ Successfully fetched {len(emails)} emails")
        
        # Show first few emails for testing
        for i, email_info in enumerate(emails[:5]):
            print(f"\n📧 Email {i+1}:")
            print(f"  Subject: {email_info['subject']}")
            print(f"  Sender: {email_info['sender']}")
            print(f"  Date: {email_info['date']}")
            print(f"  Body preview: {email_info['body'][:100]}...")
        
        return True
        
    finally:
        fetcher.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test Modular Email Fetcher')
    parser.add_argument('--test', action='store_true', help='Run test mode')
    args = parser.parse_args()
    
    if args.test:
        success = test_email_fetcher()
        sys.exit(0 if success else 1)
    else:
        success = test_email_fetcher()
        sys.exit(0 if success else 1) 