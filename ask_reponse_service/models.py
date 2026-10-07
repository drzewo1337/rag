from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from facts_service.database import Base
from datetime import datetime

class Questions(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.now)


class Answers(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    answer_text = Column(String, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    created_at = Column(DateTime, default=datetime.now)