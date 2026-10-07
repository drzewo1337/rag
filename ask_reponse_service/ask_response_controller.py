from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Annotated
from ask_reponse_service import models
from ask_reponse_service.database import SessionLocal, engine
from sqlalchemy.orm import Session


@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class QuestionCreate(BaseModel):
    question_text: str


class AnswerCreate(BaseModel):
    answer_text: str
    question_id: int


@app.post("/questions")
async def create_question(question: QuestionCreate, db: db_dependency):
    db_question = models.Questions(question_text=question.question_text)
    db.add(db_question)
    db.commit()
    return {"message": "Question created successfully", "question": db_question}


@app.post("/answers")
async def create_answer(answer: AnswerCreate, db: db_dependency):
    db_answer = models.Answers(answer_text=answer.answer_text, question_id=answer.question_id)
    db.add(db_answer)
    db.commit()
    return {"message": "Answer created successfully", "answer": db_answer}


@app.get("/questions/{question_id}")
async def get_question(question_id: int, db: db_dependency):
    db_question = db.query(models.Questions).filter(models.Questions.id == question_id).first()
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"question": db_question}


@app.get("/answers/{answer_id}")
async def get_answer(answer_id: int, db: db_dependency):
    db_answer = db.query(models.Answers).filter(models.Answers.id == answer_id).first()
    if not db_answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    return {"answer": db_answer}


@app.get("/health")
async def health_check():
    return {"status": "ok"}