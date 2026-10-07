from sqlalchemy import Column, Integer, String
from facts_service.database import Base


class Facts(Base):
    __tablename__ = "facts" 

    id = Column(Integer, primary_key=True, index=True)
    fact_text = Column(String, index=True)
    embedding = Column(String)