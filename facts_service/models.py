from sqlalchemy import Column, Integer, String, DateTime
from pgvector.sqlalchemy import Vector
from facts_service.database import Base
from embedding.embedding import EMBEDDING_DIM
from datetime import datetime


class Facts(Base):
    __tablename__ = "facts" 

    id = Column(Integer, primary_key=True, index=True)
    fact_text = Column(String, index=True)
    embedding = Column(Vector(EMBEDDING_DIM))
    created_at = Column(DateTime, default=datetime.now)