from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from embedding.embedding import EMBEDDING_DIM
from facts_service.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    content_hash = Column(String(64), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(String, nullable=False)
    page = Column(Integer, nullable=False)
    embedding = Column(Vector(EMBEDDING_DIM))
    created_at = Column(DateTime, default=datetime.now)
