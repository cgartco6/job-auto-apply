import requests
from bs4 import BeautifulSoup
import time
from config import config

def scrape_indeed_jobs(keywords, location):
    base_url = "https://www.indeed.com/jobs"
    params = {
        "q": keywords,
        "l": location,
        "sort": "date"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(base_url, params=params, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        job_cards = soup.select('.jobsearch-SerpJobCard')
        
        jobs = []
        for card in job_cards[:config.MAX_JOBS]:
            title_elem = card.select_one('.title a')
            title = title_elem.text.strip()
            company = card.select_one('.company').text.strip()
            job_url = "https://www.indeed.com" + title_elem['href']
            
            # Get job description
            time.sleep(config.SCRAPE_DELAY)
            desc = get_job_description(job_url)
            
            jobs.append({
                "title": title,
                "company": company,
                "url": job_url,
                "description": desc,
                "source": "Indeed"
            })
            
        return jobs
        
    except Exception as e:
        print(f"Scraping error: {str(e)}")
        return []

def get_job_description(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.select_one('#jobDescriptionText').text.strip()
    except:
        return ""
