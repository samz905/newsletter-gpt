

import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from processors.scheduler import NewsletterScheduler

# Global scheduler instance
scheduler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for FastAPI app"""
    global scheduler
    
    # Startup
    print("🚀 Starting Newsletter GPT Server...")
    scheduler = NewsletterScheduler()
    scheduler.start()
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Newsletter GPT Server...")
    if scheduler:
        scheduler.shutdown()

app = FastAPI(
    title="Newsletter GPT",
    description="Automated newsletter processing and digest generation",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Newsletter GPT Server is running"}

@app.get("/status")
async def get_status():
    """Get scheduler status"""
    if scheduler:
        return scheduler.get_status()
    return {"running": False, "jobs": []}

@app.post("/jobs/daily")
async def trigger_daily_job():
    """Manually trigger daily processing"""
    if scheduler:
        scheduler.run_daily_job()
        return {"message": "Daily job triggered"}
    return {"error": "Scheduler not running"}

@app.post("/jobs/weekly")
async def trigger_weekly_job():
    """Manually trigger weekly digest"""
    if scheduler:
        scheduler.run_weekly_job()
        return {"message": "Weekly job triggered"}
    return {"error": "Scheduler not running"}

def main():
    """Run the FastAPI server"""
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        access_log=False
    )

if __name__ == "__main__":
    main() 