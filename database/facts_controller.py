from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Annotated
from contextlib import asynccontextmanager
from database.dataset_loader import load_dataset
from rag_service.embedding import embed
from database import models
from database.database import SessionLocal, engine
from sqlalchemy.orm import Session


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Aplikacja startuje: inicjalizacja zasobów")
    models.Base.metadata.create_all(bind=engine)
    dataset = load_dataset()
    with SessionLocal() as db:
        for fact in dataset:
            embedding = embed(fact)
            db_fact = models.Facts(fact_text=fact, embedding=str(embedding))
            db.add(db_fact)
            db.commit()
    print("Wczytano fakty do bazy danych")
    yield



app = FastAPI(lifespan=lifespan)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class FactCreate(BaseModel):
    fact_text: str


class QuestionCreate(BaseModel):
    question_text: str


class AnswerCreate(BaseModel):
    answer_text: str
    question_id: int


@app.post("/facts")
async def create_fact(fact: FactCreate, db: db_dependency):
    db_fact = models.Facts(fact_text=fact.fact_text)
    db.add(db_fact)
    db.commit()
    return {"message": "Fact created successfully", "fact": db_fact}


# SRP: Single Responsibility Principle
@app.post("/questions")
async def create_question(question: QuestionCreate, db: db_dependency):
    db_question = models.Questions(question_text=question.question_text)
    db.add(db_question)
    db.commit()
    return {"message": "Question created successfully", "question": db_question}


# SRP: Single Responsibility Principle
@app.post("/answers")
async def create_answer(answer: AnswerCreate, db: db_dependency):
    db_answer = models.Answers(answer_text=answer.answer_text, question_id=answer.question_id)
    db.add(db_answer)
    db.commit()
    return {"message": "Answer created successfully", "answer": db_answer}


@app.get("/facts/{fact_id}")
async def get_fact(fact_id: int, db: db_dependency):
    db_fact = db.query(models.Facts).filter(models.Facts.id == fact_id).first()
    fact_text = db_fact.fact_text
    if not db_fact:
        raise HTTPException(status_code=404, detail="Fact not found")
    return {"message": "Fact found successfully", "fact": fact_text}

# SRP: Single Responsibility Principle
@app.get("/questions/{question_id}")
async def get_question(question_id: int, db: db_dependency):
    db_question = db.query(models.Questions).filter(models.Questions.id == question_id).first()
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"question": db_question}


# SRP: Single Responsibility Principle
@app.get("/answers/{answer_id}")
async def get_answer(answer_id: int, db: db_dependency):
    db_answer = db.query(models.Answers).filter(models.Answers.id == answer_id).first()
    if not db_answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    return {"answer": db_answer}


# test endpoint
@app.get("/")
def read_root():
    return {"Hello World!"}