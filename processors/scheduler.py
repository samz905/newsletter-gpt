from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from processors.daily_newsletter_processor import DailyNewsletterProcessor
from processors.weekly_digest_generator import WeeklyDigestGenerator
from processors.notion_publisher import NotionPublisher


class NewsletterScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.setup_jobs()
    
    def setup_jobs(self):
        """Setup scheduled jobs"""
        # Daily processing at 8 PM
        self.scheduler.add_job(
            self.run_daily_job,
            CronTrigger(hour=20, minute=0),  # 8:00 PM
            id='daily_processing',
            name='Daily Newsletter Processing',
            replace_existing=True
        )
        
        # Weekly digest on Sunday at 7 AM
        self.scheduler.add_job(
            self.run_weekly_job,
            CronTrigger(day_of_week='sun', hour=7, minute=0),  # Sunday 7:00 AM
            id='weekly_digest',
            name='Weekly Digest Generation',
            replace_existing=True
        )
        
        print("✅ Scheduled jobs configured:")
        print("- Daily processing: Every day at 8:00 PM")
        print("- Weekly digest: Every Sunday at 7:00 AM")
    
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            print("🚀 Scheduler started")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("🛑 Scheduler stopped")
    
    def get_status(self):
        """Get scheduler status"""
        jobs = self.scheduler.get_jobs()
        return {
            'running': self.scheduler.running,
            'jobs': [{'id': job.id, 'name': job.name, 'next_run': str(job.next_run_time)} for job in jobs]
        }
    
    def run_daily_job(self):
        """Run daily newsletter processing"""
        print("🚀 Starting Daily Newsletter Processing...")
        
        try:
            processor = DailyNewsletterProcessor()
            results = processor.run_daily_processing()
            
            if results.get('success'):
                processed_count = results.get('newsletters_processed', 0)
                duration = results.get('processing_time', 0)
                print(f"✅ Daily processing completed: {processed_count} newsletters in {duration:.2f}s")
            else:
                error_msg = results.get('error', 'Unknown error')
                print(f"❌ Daily processing failed: {error_msg}")
                
        except Exception as e:
            print(f"❌ Daily job error: {e}")
    
    def run_weekly_job(self):
        """Run weekly digest generation"""
        print("🚀 Starting Weekly Digest Generation...")
        
        try:
            generator = WeeklyDigestGenerator()
            digest_path = generator.generate_weekly_digest()
            
            if digest_path:
                print("✅ Weekly digest generated")
                
                # Try to publish to Notion
                try:
                    notion_publisher = NotionPublisher()
                    digest_data = self._create_digest_data_for_notion(digest_path)
                    
                    if digest_data:
                        page_id = notion_publisher.publish_weekly_digest(digest_data)
                        if page_id:
                            print(f"✅ Published to Notion: {page_id}")
                        else:
                            print("⚠️ Notion publishing failed")
                            
                except Exception as e:
                    print(f"❌ Notion error: {e}")
            else:
                print("❌ Weekly digest generation failed")
                
        except Exception as e:
            print(f"❌ Weekly job error: {e}")
    
    def _create_digest_data_for_notion(self, digest_path):
        """Create basic digest data for Notion publishing"""
        return {
            'week_start': datetime.now().strftime('%Y-%m-%d'),
            'week_end': datetime.now().strftime('%Y-%m-%d'),
            'total_newsletters': 0,
            'genre_summaries': {},
            'unified_summary': 'Weekly digest generated'
        } 