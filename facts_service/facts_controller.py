import hashlib
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from embedding.embedding import embed
from facts_service import models
from facts_service.database import SessionLocal, engine
from facts_service.pdf_chunks import MAX_CHUNKS, MAX_PDF_BYTES, extract_chunks


def prepare_database():
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.execute(text("DROP TABLE IF EXISTS facts"))
    models.Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Aplikacja startuje: inicjalizacja zasobów")
    prepare_database()
    yield


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def reject_oversized_upload(request: Request, call_next):
    if request.method == "POST" and request.url.path == "/documents":
        raw_length = request.headers.get("content-length")
        if raw_length is not None:
            try:
                announced = int(raw_length)
            except ValueError:
                announced = 0
            if announced > MAX_PDF_BYTES + 1024 * 1024:
                return JSONResponse(status_code=413, content={"detail": "File exceeds 50 MB"})
    return await call_next(request)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def read_upload(file: UploadFile, limit: int) -> bytes:
    blocks = []
    total = 0
    while True:
        block = file.file.read(1024 * 1024)
        if not block:
            break
        total += len(block)
        if total > limit:
            raise HTTPException(status_code=413, detail="File exceeds 50 MB")
        blocks.append(block)
    return b"".join(blocks)


def pdf_filename(raw_name: str | None) -> str:
    name = Path(str(raw_name or "").replace("\\", "/")).name.strip()
    return name or "document.pdf"


def duplicate_message(db: Session, content_hash: str) -> str:
    existing = db.query(models.Document).filter(models.Document.content_hash == content_hash).first()
    if existing is None:
        return "This file is already uploaded"
    return f"This file is already uploaded as {existing.filename}"


@app.get("/documents")
def list_documents(db: db_dependency):
    documents = db.query(models.Document).order_by(models.Document.id.desc()).all()
    counts = dict(
        db.query(models.Chunk.document_id, func.count(models.Chunk.id))
        .group_by(models.Chunk.document_id)
        .all()
    )
    return {
        "documents": [
            {
                "id": document.id,
                "filename": document.filename,
                "size_bytes": document.size_bytes,
                "chunk_count": int(counts.get(document.id, 0)),
                "created_at": document.created_at,
            }
            for document in documents
        ]
    }


@app.post("/documents")
def create_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    data = read_upload(file, MAX_PDF_BYTES)
    if b"%PDF" not in data[:1024]:
        raise HTTPException(status_code=400, detail="File is not a PDF")

    content_hash = hashlib.sha256(data).hexdigest()
    existing = db.query(models.Document).filter(models.Document.content_hash == content_hash).first()
    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail=f"This file is already uploaded as {existing.filename}",
        )

    try:
        pieces = extract_chunks(data)
    except Exception as exc:
        print(f"PDF read failed: {exc}")
        raise HTTPException(status_code=400, detail="Could not read PDF") from exc

    if not pieces:
        raise HTTPException(status_code=400, detail="PDF has no text")
    if len(pieces) > MAX_CHUNKS:
        raise HTTPException(status_code=400, detail="PDF has too many text chunks (max 200)")

    try:
        vectors = [embed(content) for _, content in pieces]
    except Exception as exc:
        print(f"Embedding failed: {exc}")
        raise HTTPException(status_code=503, detail="Embedding failed") from exc

    document = models.Document(
        filename=pdf_filename(file.filename),
        size_bytes=len(data),
        content_hash=content_hash,
        created_at=datetime.now(),
    )
    try:
        db.add(document)
        db.flush()
        for (page, content), vector in zip(pieces, vectors):
            db.add(
                models.Chunk(
                    document_id=document.id,
                    content=content,
                    page=page,
                    embedding=vector,
                    created_at=datetime.now(),
                )
            )
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=duplicate_message(db, content_hash)) from None
    except Exception:
        db.rollback()
        raise

    db.refresh(document)
    return {
        "id": document.id,
        "filename": document.filename,
        "size_bytes": document.size_bytes,
        "chunk_count": len(pieces),
        "created_at": document.created_at,
    }


@app.delete("/documents/{document_id}")
def delete_document(document_id: int, db: db_dependency):
    document = db.get(models.Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(document)
    db.commit()
    return {"message": "Document deleted"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}
