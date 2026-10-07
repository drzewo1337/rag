from sqlalchemy import Column, Integer, String, ForeignKey
from facts_service.database import Base


class Questions(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, index=True)


class Answers(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    answer_text = Column(String, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"))