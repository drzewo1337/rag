from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Annotated
from contextlib import asynccontextmanager
from facts_service.dataset_loader import load_dataset
from embedding.embedding import embed
from facts_service import models
from facts_service.database import SessionLocal, engine
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime


def prepare_facts_table():
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        column_type = conn.execute(text(
            """
            SELECT udt_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'facts'
              AND column_name = 'embedding'
            """
        )).scalar()
        if column_type is not None and column_type != "vector":
            print("Kolumna embedding nie jest typu vector — odtwarzam tabelę facts")
            conn.execute(text("DROP TABLE facts"))
    models.Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Aplikacja startuje: inicjalizacja zasobów")
    prepare_facts_table()
    with SessionLocal() as db:
        if db.query(models.Facts).count() > 0:
            print("Fakty już są w bazie — pomijam bootstrap")
        else:
            dataset = load_dataset()
            for fact in dataset:
                embedding = embed(fact)
                db_fact = models.Facts(fact_text=fact, embedding=embedding, created_at=datetime.now())
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


@app.get("/facts")
async def list_facts(db: db_dependency):
    db_facts = db.query(models.Facts).order_by(models.Facts.id.desc()).all()
    return {
        "count": len(db_facts),
        "facts": [
            {"id": fact.id, "fact_text": fact.fact_text, "created_at": fact.created_at}
            for fact in db_facts
        ],
    }


@app.post("/facts")
async def create_fact(fact: FactCreate, db: db_dependency):
    db_fact = models.Facts(fact_text=fact.fact_text, created_at=datetime.now())
    db.add(db_fact)
    db.commit()
    return {"message": "Fact created successfully", "fact": db_fact}


@app.get("/facts/{fact_id}")
async def get_fact(fact_id: int, db: db_dependency):
    db_fact = db.query(models.Facts).filter(models.Facts.id == fact_id).first()
    fact_text = db_fact.fact_text
    if not db_fact:
        raise HTTPException(status_code=404, detail="Fact not found")
    return {"message": "Fact found successfully", "fact": fact_text}


@app.get("/health")
async def health_check():
    return {"status": "ok"}