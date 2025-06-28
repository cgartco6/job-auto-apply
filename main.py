from scraper.indeed_scraper import scrape_indeed_jobs
from ai_tools.cv_rewriter import CVRewriter
from ai_tools.cover_generator import CoverGenerator
from email_system.email_sender import EmailSender
from database.job_tracker import JobTracker
from config import config
import time
from telegram_bot.bot_handler import telegram_bot
import threading

def start_telegram_bot():
    """Start Telegram bot in a separate thread"""
    telegram_bot.run()

def main():
    # Start Telegram bot in background thread
    bot_thread = threading.Thread(target=start_telegram_bot, daemon=True)
    bot_thread.start()
    
    # Notify startup
    telegram_bot.application.bot.send_message(
        chat_id=config.TELEGRAM_CHAT_ID,
        text="🤖 Job Search System Activated\n"
             "I'm now searching for jobs in South Africa..."
    )
    
    # ... existing job search code ...
    
    # When finding a job
    for job in jobs:
        # Notify user about job found
        await telegram_bot.notify_new_job(job)
        
        # ... application processing ...
        
        # After sending application
        await telegram_bot.notify_application_sent(job, success=True)
    
    # When job offer received
    if tracker.has_job_offer():
        await telegram_bot.notify_job_offer(job_info) 
                                           
if __name__ == "__main__":
    main()
def main():
    # Initialize components
    cv_rewriter = CVRewriter()
    cover_gen = CoverGenerator()
    email_sender = EmailSender()
    tracker = JobTracker()
    
    # Load base documents
    with open(config.BASE_CV, 'r') as f:
        base_cv = f.read()
    with open(config.BASE_COVER, 'r') as f:
        base_cover = f.read()
    
    # Scrape jobs
    jobs = scrape_indeed_jobs("Python Developer", "Remote")
    print(f"Found {len(jobs)} jobs")
    
    for job in jobs:
        print(f"Processing: {job['title']} at {job['company']}")
        
        # AI customization
        custom_cv = cv_rewriter.rewrite(base_cv, job['description'])
        custom_cover = cover_gen.generate(job, base_cover)
        
        # Send application
        if email_sender.send_application(job, custom_cv, custom_cover):
            print("Application sent")
            tracker.record_application(job)
        else:
            print("Application failed")
            tracker.record_application(job, status="failed")
        
        time.sleep(config.SCRAPE_DELAY)

if __name__ == "__main__":
    main()
