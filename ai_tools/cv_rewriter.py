from transformers import pipeline
import time
from config import config

class CVRewriter:
    def __init__(self):
        self.model = pipeline(
            "text2text-generation", 
            model=config.CV_MODEL,
            max_length=1024
        )
        
    def rewrite(self, base_cv, job_description):
        prompt = f"""
        Rewrite this resume for a {job_description[:300]} position:
        {base_cv}
        """
        
        for _ in range(3):  # Retry mechanism
            try:
                return self.model(prompt)[0]['generated_text']
            except Exception as e:
                print(f"CV rewrite error: {str(e)}")
                time.sleep(2)
        return base_cv  # Fallback to original
