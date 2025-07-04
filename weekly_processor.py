import argparse
from typing import Optional
from datetime import datetime
from email_processing.email_fetcher import EmailFetcher
from processors.email_filters import EmailFilters
from processors.newsletter_identifier import NewsletterIdentifier
from processors.content_cleaner import ContentCleaner
from processors.summary_generator import SummaryGenerator
from processors.digest_formatter import DigestFormatter
import os
from dotenv import load_dotenv

load_dotenv()

class WeeklyProcessor:
    """Orchestrates the weekly newsletter processing pipeline"""
    
    def __init__(self):
        self.email_fetcher = None
        self.email_filters = EmailFilters()
        self.newsletter_identifier = NewsletterIdentifier()
        self.content_cleaner = ContentCleaner()
        self.summary_generator = SummaryGenerator()
        self.digest_formatter = DigestFormatter()
    
    def setup_email_fetcher(self) -> bool:
        """Setup email fetcher with credentials"""
        email_address = os.getenv("EMAIL_ADDRESS")
        email_password = os.getenv("EMAIL_PASSWORD")
        
        if not email_address or not email_password:
            print("❌ Email credentials not found in environment variables")
            return False
        
        self.email_fetcher = EmailFetcher(email_address, email_password)
        return self.email_fetcher.connect()
    
    def save_digest_to_file(self, digest: str) -> str:
        """Save digest to a file and return filename"""
        # Create digests directory if it doesn't exist
        os.makedirs("digests", exist_ok=True)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"digests/newsletter_digest_{timestamp}.md"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(digest)
            
            print(f"✅ Digest saved to: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error saving digest: {e}")
            return ""
    
    def process_weekly_digest(self, dry_run: bool = False) -> Optional[str]:
        """Run the complete weekly processing pipeline"""
        print("🚀 Starting weekly digest processing...")
        
        try:
            # Setup email fetcher
            if not self.setup_email_fetcher():
                return None
            
            # 1. Fetch emails
            print("📧 Fetching emails from the past 7 days...")
            emails = self.email_fetcher.fetch_emails_from_last_7_days()
            if not emails:
                print("❌ No emails found")
                return None
            
            print(f"✅ Found {len(emails)} emails")
            
            # 2. Apply primitive filtering
            filtered_emails = self.email_filters.apply_primitive_filtering(emails)
            if not filtered_emails:
                print("❌ No emails passed primitive filtering")
                return None
            
            # 3. LLM newsletter identification (now with semantic context)
            newsletter_emails = self.newsletter_identifier.identify_newsletters(filtered_emails)
            if not newsletter_emails:
                print("❌ No newsletters identified by LLM")
                return None
            
            # 4. Clean content
            cleaned_newsletters = self.content_cleaner.clean_newsletters(newsletter_emails)
            
            # 5. Generate summaries
            summaries = self.summary_generator.generate_summaries(cleaned_newsletters)
            if not summaries:
                print("❌ No summaries generated")
                return None
            
            # 6. Create weekly digest
            digest = self.digest_formatter.create_weekly_digest(summaries)
            
            # 7. Save digest to file (always create the file)
            filename = self.save_digest_to_file(digest)
            
            # Print processing statistics
            print("\n📊 PROCESSING SUMMARY")
            print("=" * 30)
            print(f"📥 Total emails fetched: {len(emails)}")
            print(f"🔍 After primitive filtering: {len(filtered_emails)}")
            print(f"🤖 Newsletters identified: {len(newsletter_emails)}")
            print(f"📝 Summaries generated: {len(summaries)}")
            print(f"📄 Digest file created: {filename}")
            print("=" * 30)
            
            if dry_run:
                print("\n" + "="*50)
                print("DRY RUN - WEEKLY DIGEST PREVIEW")
                print("="*50)
                print(digest)
                print("="*50)
                if filename:
                    print(f"📄 Full digest saved to: {filename}")
            else:
                print(f"📄 Weekly digest created: {filename}")
                print(f"📊 Processed {len(summaries)} newsletters successfully!")
            
            return digest
            
        except Exception as e:
            print(f"❌ Processing error: {e}")
            return None
        
        finally:
            if self.email_fetcher:
                self.email_fetcher.disconnect()

def main():
    parser = argparse.ArgumentParser(description='Weekly Newsletter Processor')
    parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode (shows preview but still saves file)')
    args = parser.parse_args()
    
    processor = WeeklyProcessor()
    digest = processor.process_weekly_digest(dry_run=args.dry_run)
    
    if digest:
        print("✅ Weekly digest processing completed successfully!")
    else:
        print("❌ Weekly digest processing failed!")

if __name__ == "__main__":
    main()
 