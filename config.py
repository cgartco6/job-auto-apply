import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    
    # Telegram
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # Your personal chat ID
    
    # Email settings
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASS = os.getenv("EMAIL_PASS")
    
    # AI models
    CV_MODEL = "t5-small"
    COVER_MODEL = "facebook/bart-base"
    
    # Scraping
    SCRAPE_DELAY = 5  # seconds
    MAX_JOBS = 20
    
    # Files
    BASE_CV = "base_cv.txt"
    BASE_COVER = "cover_template.txt"
    
    # Database
    DB_PATH = "jobs.db"

config = Config()
