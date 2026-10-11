import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from messaging import QUESTIONS_QUEUE, consume_queue
from rag_service.pipeline import generate_answer, process_question_message

logger = logging.getLogger(__name__)

_consumer_thread: threading.Thread | None = None


def _run_consumer() -> None:
    consume_queue(QUESTIONS_QUEUE, process_question_message)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _consumer_thread
    _consumer_thread = threading.Thread(
        target=_run_consumer,
        name="rabbit-questions-consumer",
        daemon=True,
    )
    _consumer_thread.start()
    logger.info("rag_service consumer started on queue=%s", QUESTIONS_QUEUE)
    yield
    logger.info("rag_service shutting down (consumer thread is daemon)")


app = FastAPI(lifespan=lifespan)


class AnswerRequest(BaseModel):
    question_text: str


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/answer")
async def answer_debug(body: AnswerRequest):
    """Synchronous debug endpoint — production flow uses the questions queue."""
    text = generate_answer(body.question_text)
    return {"answer": text}
