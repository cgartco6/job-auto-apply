from transformers import pipeline
import time
from config import config

class CoverGenerator:
    def __init__(self):
        self.model = pipeline(
            "text2text-generation",
            model=config.COVER_MODEL,
            max_length=512
        )
        
    def generate(self, job_info, base_cover):
        prompt = f"""
        Create a cover letter for {job_info['title']} position at {job_info['company']}:
        Job Description: {job_info['description'][:500]}
        ---
        Base Cover Letter: {base_cover}
        """
        
        for _ in range(3):  # Retry mechanism
            try:
                return self.model(prompt)[0]['generated_text']
            except Exception as e:
                print(f"Cover generation error: {str(e)}")
                time.sleep(2)
        return base_cover  # Fallback to template
