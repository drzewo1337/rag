from sqlalchemy import Column, Integer, String, DateTime    
from facts_service.database import Base
from datetime import datetime


class Facts(Base):
    __tablename__ = "facts" 

    id = Column(Integer, primary_key=True, index=True)
    fact_text = Column(String, index=True)
    embedding = Column(String)
    created_at = Column(DateTime, default=datetime.now)