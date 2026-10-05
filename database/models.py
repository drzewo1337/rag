from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class Facts(Base):
    __tablename__ = "facts"

    id = Column(Integer, primary_key=True, index=True)
    fact_text = Column(String, index=True)


class Questions(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, index=True)


class Answers(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    answer_text = Column(String, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"))