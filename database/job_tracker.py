from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import config

Base = declarative_base()

class JobApplication(Base):
    __tablename__ = 'applications'
    
    id = Column(Integer, primary_key=True)
    job_title = Column(String(200))
    company = Column(String(100))
    status = Column(String(20), default='submitted')
    applied_date = Column(String(20))
    response = Column(Text)

class JobTracker:
    def __init__(self):
        self.engine = create_engine(f"sqlite:///{config.DB_PATH}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
    def record_application(self, job_info, status="submitted"):
        session = self.Session()
        application = JobApplication(
            job_title=job_info['title'],
            company=job_info['company'],
            status=status
        )
        session.add(application)
        session.commit()
        session.close()
