import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ask_reponse_service import models
from ask_reponse_service.database import SessionLocal, engine
from messaging import QUESTIONS_QUEUE, RabbitMQConnection

logger = logging.getLogger(__name__)

_rabbit: RabbitMQConnection | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _rabbit
    models.Base.metadata.create_all(bind=engine)
    _rabbit = RabbitMQConnection()
    _rabbit.declare_queue(QUESTIONS_QUEUE)
    logger.info("ask_response_service ready (publisher on %s)", QUESTIONS_QUEUE)
    yield
    if _rabbit is not None:
        _rabbit.close()
        _rabbit = None


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
    if _rabbit is None:
        raise HTTPException(status_code=503, detail="Message broker not ready")

    db_question = models.Questions(
        question_text=question.question_text,
        created_at=datetime.now(),
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)

    _rabbit.publish_json(
        QUESTIONS_QUEUE,
        {
            "question_id": db_question.id,
            "question_text": db_question.question_text,
        },
    )

    return {
        "message": "Question created successfully",
        "question": db_question,
    }


@app.post("/answers")
async def create_answer(answer: AnswerCreate, db: db_dependency):
    db_answer = models.Answers(
        answer_text=answer.answer_text,
        question_id=answer.question_id,
        created_at=datetime.now(),
    )
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    return {"message": "Answer created successfully", "answer": db_answer}


@app.get("/questions/{question_id}")
async def get_question(question_id: int, db: db_dependency):
    db_question = db.query(models.Questions).filter(models.Questions.id == question_id).first()
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"question": db_question}


@app.get("/questions/{question_id}/answers")
async def get_answers_for_question(question_id: int, db: db_dependency):
    db_answers = (
        db.query(models.Answers)
        .filter(models.Answers.question_id == question_id)
        .order_by(models.Answers.created_at.desc())
        .all()
    )
    return {"question_id": question_id, "answers": db_answers}


@app.get("/answers/{answer_id}")
async def get_answer(answer_id: int, db: db_dependency):
    db_answer = db.query(models.Answers).filter(models.Answers.id == answer_id).first()
    if not db_answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    return {"answer": db_answer}


@app.get("/health")
async def health_check():
    return {"status": "ok"}
