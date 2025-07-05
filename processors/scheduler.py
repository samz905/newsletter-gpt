"""
Newsletter GPT Scheduler
Handles automated daily and weekly processing with APScheduler
"""

import os
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from dotenv import load_dotenv

# Import our processors
from processors.daily_newsletter_processor import DailyNewsletterProcessor
from processors.weekly_digest_generator import WeeklyDigestGenerator
from processors.notion_publisher import NotionPublisher

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('newsletter_gpt.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NewsletterScheduler:
    """
    Main scheduler for Newsletter GPT automation
    """
    
    def __init__(self):
        """Initialize scheduler and processors"""
        self.scheduler = BlockingScheduler()
        self.daily_processor = DailyNewsletterProcessor()
        self.weekly_generator = WeeklyDigestGenerator()
        self.notion_publisher = NotionPublisher()
        
        # Add job listeners
        self.scheduler.add_listener(self._job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        
        # Setup jobs
        self._setup_jobs()
        
        logger.info("Newsletter GPT Scheduler initialized")
    
    def _setup_jobs(self):
        """Setup daily and weekly scheduled jobs"""
        
        # Daily job: Process emails at 8 PM every day
        self.scheduler.add_job(
            func=self._daily_job,
            trigger=CronTrigger(hour=20, minute=0),  # 8 PM
            id='daily_newsletter_processing',
            name='Daily Newsletter Processing',
            replace_existing=True,
            misfire_grace_time=3600  # 1 hour grace period
        )
        
        # Weekly job: Generate digest on Sunday at 7 AM
        self.scheduler.add_job(
            func=self._weekly_job,
            trigger=CronTrigger(day_of_week='sun', hour=7, minute=0),  # Sunday 7 AM
            id='weekly_digest_generation',
            name='Weekly Digest Generation',
            replace_existing=True,
            misfire_grace_time=7200  # 2 hour grace period
        )
        
        # Optional: Test job for immediate execution (remove in production)
        # self.scheduler.add_job(
        #     func=self._test_job,
        #     trigger='interval',
        #     minutes=5,
        #     id='test_job',
        #     name='Test Job'
        # )
        
        logger.info("Scheduled jobs configured:")
        logger.info("- Daily processing: Every day at 8:00 PM")
        logger.info("- Weekly digest: Every Sunday at 7:00 AM")
    
    def _daily_job(self):
        """
        Daily job: Process last 24 hours of emails
        """
        try:
            logger.info("=== STARTING DAILY NEWSLETTER PROCESSING ===")
            start_time = datetime.now()
            
            # Run daily newsletter processing
            result = self.daily_processor.process_daily_newsletters()
            
            # Log results
            end_time = datetime.now()
            duration = end_time - start_time
            
            if result:
                processed_count = result.get('processed_count', 0)
                logger.info(f"✅ Daily processing completed successfully")
                logger.info(f"📊 Processed {processed_count} newsletters")
                logger.info(f"⏱️ Duration: {duration}")
                
                # Send success notification (optional)
                self._send_notification(
                    f"Daily Newsletter Processing Complete",
                    f"Successfully processed {processed_count} newsletters in {duration}"
                )
            else:
                logger.error("❌ Daily processing failed")
                self._send_notification(
                    "Daily Newsletter Processing Failed",
                    "Daily processing encountered an error. Check logs for details."
                )
                
        except Exception as e:
            logger.error(f"Fatal error in daily job: {e}", exc_info=True)
            self._send_notification(
                "Daily Newsletter Processing Error",
                f"Fatal error occurred: {str(e)}"
            )
    
    def _weekly_job(self):
        """
        Weekly job: Generate and publish weekly digest
        """
        try:
            logger.info("=== STARTING WEEKLY DIGEST GENERATION ===")
            start_time = datetime.now()
            
            # Generate weekly digest
            digest_result = self.weekly_generator.generate_weekly_digest()
            
            if digest_result:
                logger.info("✅ Weekly digest generated successfully")
                
                # Publish to Notion
                try:
                    # Extract data for Notion
                    week_start = digest_result.get('week_start')
                    week_end = digest_result.get('week_end')
                    total_newsletters = digest_result.get('total_newsletters', 0)
                    
                    # Parse genre summaries from the digest
                    genre_summaries = self._parse_genre_summaries(digest_result)
                    unified_summary = digest_result.get('unified_summary', '')
                    
                    notion_data = {
                        'week_start': week_start,
                        'week_end': week_end,
                        'total_newsletters': total_newsletters,
                        'genre_summaries': genre_summaries,
                        'unified_summary': unified_summary
                    }
                    
                    page_id = self.notion_publisher.publish_weekly_digest(notion_data)
                    
                    if page_id:
                        logger.info(f"✅ Weekly digest published to Notion: {page_id}")
                    else:
                        logger.warning("⚠️ Weekly digest generation successful but Notion publishing failed")
                        
                except Exception as e:
                    logger.error(f"Error publishing to Notion: {e}")
                
                # Log results
                end_time = datetime.now()
                duration = end_time - start_time
                
                logger.info(f"📊 Weekly digest covers {total_newsletters} newsletters")
                logger.info(f"⏱️ Duration: {duration}")
                
                # Send success notification
                self._send_notification(
                    f"Weekly Digest Generation Complete",
                    f"Successfully generated weekly digest for {total_newsletters} newsletters"
                )
            else:
                logger.error("❌ Weekly digest generation failed")
                self._send_notification(
                    "Weekly Digest Generation Failed",
                    "Weekly digest generation encountered an error. Check logs for details."
                )
                
        except Exception as e:
            logger.error(f"Fatal error in weekly job: {e}", exc_info=True)
            self._send_notification(
                "Weekly Digest Generation Error",
                f"Fatal error occurred: {str(e)}"
            )
    
    def _parse_genre_summaries(self, digest_result):
        """
        Parse genre summaries from weekly digest result
        This is a simplified parser - enhance based on actual digest structure
        """
        genre_summaries = {}
        
        # Try to extract genre data from digest result
        if 'genre_data' in digest_result:
            genre_data = digest_result['genre_data']
            for genre, data in genre_data.items():
                genre_summaries[genre] = {
                    'summary': data.get('summary', ''),
                    'newsletters': data.get('newsletters', [])
                }
        
        return genre_summaries
    
    def _test_job(self):
        """Test job for debugging (remove in production)"""
        logger.info("🧪 Test job executed successfully")
    
    def _job_listener(self, event):
        """Listen to job events for monitoring"""
        if event.exception:
            logger.error(f"Job {event.job_id} crashed: {event.exception}")
        else:
            logger.info(f"Job {event.job_id} executed successfully")
    
    def _send_notification(self, subject: str, message: str):
        """
        Send notification (email, Slack, etc.)
        Implement based on your notification preferences
        """
        # For now, just log the notification
        logger.info(f"NOTIFICATION: {subject} - {message}")
        
        # TODO: Implement actual notification system
        # Examples:
        # - Send email
        # - Post to Slack
        # - Send push notification
        # - Write to monitoring system
    
    def start(self):
        """Start the scheduler"""
        logger.info("🚀 Starting Newsletter GPT Scheduler...")
        logger.info("Press Ctrl+C to stop the scheduler")
        
        try:
            self.scheduler.start()
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {e}", exc_info=True)
        finally:
            self.scheduler.shutdown()
            logger.info("Scheduler shut down")
    
    def stop(self):
        """Stop the scheduler"""
        logger.info("🛑 Stopping Newsletter GPT Scheduler...")
        self.scheduler.shutdown()
    
    def get_jobs(self):
        """Get list of scheduled jobs"""
        return self.scheduler.get_jobs()
    
    def run_daily_job_now(self):
        """Run daily job immediately (for testing)"""
        logger.info("🧪 Running daily job manually...")
        self._daily_job()
    
    def run_weekly_job_now(self):
        """Run weekly job immediately (for testing)"""
        logger.info("🧪 Running weekly job manually...")
        self._weekly_job()

# Main entry point
if __name__ == "__main__":
    scheduler = NewsletterScheduler()
    
    # Optional: Run a test job immediately
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test-daily":
            scheduler.run_daily_job_now()
        elif sys.argv[1] == "--test-weekly":
            scheduler.run_weekly_job_now()
        elif sys.argv[1] == "--list-jobs":
            jobs = scheduler.get_jobs()
            print(f"Scheduled jobs ({len(jobs)}):")
            for job in jobs:
                print(f"  - {job.id}: {job.name}")
        else:
            print("Usage: python scheduler.py [--test-daily|--test-weekly|--list-jobs]")
    else:
        # Start the scheduler
        scheduler.start() 