#!/usr/bin/env python3
"""
Newsletter GPT - Main Application Entry Point
Production-ready application with monitoring, logging, and error handling
"""

import os
import sys
import logging
import signal
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import psutil

# Import our core components
from processors.scheduler import NewsletterScheduler
from processors.notion_publisher import NotionPublisher
from processors.daily_newsletter_processor import DailyNewsletterProcessor
from processors.weekly_digest_generator import WeeklyDigestGenerator

# Load environment variables
load_dotenv()

# Configure logging
def setup_logging():
    """Setup comprehensive logging configuration"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # File handler for all logs
    file_handler = logging.FileHandler(log_dir / 'newsletter_gpt.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = logging.FileHandler(log_dir / 'newsletter_gpt_errors.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    return logging.getLogger(__name__)

class NewsletterGPTApp:
    """
    Main Newsletter GPT Application
    """
    
    def __init__(self):
        """Initialize the application"""
        self.logger = setup_logging()
        self.scheduler = None
        self.running = False
        self.start_time = datetime.now()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info("Newsletter GPT Application initialized")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.shutdown()
    
    def check_dependencies(self):
        """Check system dependencies and environment"""
        self.logger.info("Checking system dependencies...")
        
        # Check environment variables
        required_env_vars = [
            'EMAIL_ADDRESS',
            'EMAIL_PASSWORD',
            'OPENROUTER_API_KEY',
            'NOTION_TOKEN',
            'NOTION_DATABASE_ID'
        ]
        
        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        # Check system resources
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        self.logger.info(f"System resources:")
        self.logger.info(f"  Memory: {memory.percent}% used ({memory.available / (1024**3):.1f}GB available)")
        self.logger.info(f"  Disk: {disk.percent}% used ({disk.free / (1024**3):.1f}GB free)")
        
        if memory.percent > 90:
            self.logger.warning("High memory usage detected")
        
        if disk.percent > 90:
            self.logger.warning("Low disk space detected")
        
        return True
    
    def test_components(self):
        """Test all components before starting"""
        self.logger.info("Testing components...")
        
        try:
            # Test Notion connection
            notion_publisher = NotionPublisher()
            if not notion_publisher.test_connection():
                self.logger.error("Notion connection test failed")
                return False
            
            # Test database connection
            from processors.sqlite_manager import SQLiteManager
            db_manager = SQLiteManager()
            db_manager.connect()
            db_manager.create_tables()
            db_manager.disconnect()
            
            self.logger.info("All component tests passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Component test failed: {e}")
            return False
    
    def start_scheduler(self):
        """Start the scheduler"""
        try:
            self.logger.info("Starting Newsletter GPT Scheduler...")
            self.scheduler = NewsletterScheduler()
            self.running = True
            
            # Log scheduler info
            jobs = self.scheduler.get_jobs()
            self.logger.info(f"Scheduler started with {len(jobs)} jobs:")
            for job in jobs:
                self.logger.info(f"  - {job.id}: {job.name}")
            
            # Start the scheduler
            self.scheduler.start()
            
        except Exception as e:
            self.logger.error(f"Failed to start scheduler: {e}")
            self.running = False
            raise
    
    def run_manual_job(self, job_type: str):
        """Run a manual job for testing"""
        self.logger.info(f"Running manual {job_type} job...")
        
        try:
            if job_type == "daily":
                processor = DailyNewsletterProcessor()
                result = processor.process_daily_newsletters()
                self.logger.info(f"Daily job completed: {result}")
            elif job_type == "weekly":
                generator = WeeklyDigestGenerator()
                result = generator.generate_weekly_digest()
                self.logger.info(f"Weekly job completed: {result}")
            else:
                self.logger.error(f"Unknown job type: {job_type}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Manual job failed: {e}")
            return False
    
    def get_status(self):
        """Get application status"""
        uptime = datetime.now() - self.start_time
        memory = psutil.virtual_memory()
        process = psutil.Process()
        
        status = {
            'running': self.running,
            'uptime': str(uptime),
            'memory_usage': f"{memory.percent}%",
            'process_memory': f"{process.memory_info().rss / (1024**2):.1f}MB",
            'cpu_percent': f"{process.cpu_percent()}%"
        }
        
        if self.scheduler:
            jobs = self.scheduler.get_jobs()
            status['scheduled_jobs'] = len(jobs)
            status['jobs'] = [{'id': job.id, 'name': job.name} for job in jobs]
        
        return status
    
    def shutdown(self):
        """Shutdown the application gracefully"""
        self.logger.info("Shutting down Newsletter GPT...")
        
        if self.scheduler:
            self.scheduler.stop()
        
        self.running = False
        self.logger.info("Shutdown complete")
    
    def run(self):
        """Main application run method"""
        self.logger.info("=== Newsletter GPT Starting ===")
        
        try:
            # Check dependencies
            if not self.check_dependencies():
                self.logger.error("Dependency check failed, exiting")
                return 1
            
            # Test components
            if not self.test_components():
                self.logger.error("Component test failed, exiting")
                return 1
            
            # Start scheduler
            self.start_scheduler()
            
            return 0
            
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
            return 0
        except Exception as e:
            self.logger.error(f"Application error: {e}", exc_info=True)
            return 1
        finally:
            self.shutdown()

def main():
    """Main entry point"""
    app = NewsletterGPTApp()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "start":
            return app.run()
        elif command == "test-daily":
            return 0 if app.run_manual_job("daily") else 1
        elif command == "test-weekly":
            return 0 if app.run_manual_job("weekly") else 1
        elif command == "test-components":
            return 0 if app.test_components() else 1
        elif command == "status":
            print(app.get_status())
            return 0
        elif command == "help":
            print("Newsletter GPT Commands:")
            print("  start         - Start the scheduler")
            print("  test-daily    - Run daily job manually")
            print("  test-weekly   - Run weekly job manually")
            print("  test-components - Test all components")
            print("  status        - Show application status")
            print("  help          - Show this help message")
            return 0
        else:
            print(f"Unknown command: {command}")
            print("Use 'python app.py help' for available commands")
            return 1
    else:
        # Default: start the application
        return app.run()

if __name__ == "__main__":
    sys.exit(main()) 