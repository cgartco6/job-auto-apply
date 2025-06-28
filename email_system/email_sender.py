import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from config import config

class EmailSender:
    def __init__(self):
        self.server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        self.server.login(config.EMAIL_USER, config.EMAIL_PASS)
        
    def send_application(self, job_info, cv_text, cover_text):
        msg = MIMEMultipart()
        msg['Subject'] = f"Application for {job_info['title']} Position"
        msg['From'] = config.EMAIL_USER
        msg['To'] = "hiring@company.com"  # Should be extracted in real implementation
        
        # Email body
        msg.attach(MIMEText(cover_text, 'plain'))
        
        # Attach CV
        cv_attachment = MIMEApplication(cv_text.encode('utf-8'), Name="resume.txt")
        cv_attachment['Content-Disposition'] = 'attachment; filename="resume.txt"'
        msg.attach(cv_attachment)
        
        # Send with retries
        for attempt in range(3):
            try:
                self.server.send_message(msg)
                return True
            except Exception as e:
                print(f"Email error (attempt {attempt+1}): {str(e)}")
                time.sleep(5)
        return False
