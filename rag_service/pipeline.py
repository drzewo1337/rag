import logging
import os

import httpx
import ollama

from rag_service.retrieve import retrieve


logger = logging.getLogger(__name__)


LANGUAGE_MODEL = "hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF"


def generate_answer(question_text: str) -> str:
    retrieved_knowledge = retrieve(question_text)
    context_lines = "\n".join(
        f" - (similarity: {similarity:.2f}) {chunk}"
        for chunk, similarity in retrieved_knowledge
    )
    instruction_prompt = f"""You are a helpful chatbot.
Use only the following pieces of context to answer the question. Don't make up any new information:
{context_lines}
"""
    response = ollama.chat(
        model=LANGUAGE_MODEL,
        messages=[
            {"role": "system", "content": instruction_prompt},
            {"role": "user", "content": question_text},
        ],
    )
    return response["message"]["content"]


def save_answer_to_ask_service(question_id: int, answer_text: str) -> None:
    base_url = os.getenv("ASK_RESPONSE_SERVICE_URL", "http://ask_response_service:8001")
    url = f"{base_url.rstrip('/')}/answers"
    with httpx.Client(timeout=300.0) as client:
        response = client.post(
            url,
            json={"question_id": question_id, "answer_text": answer_text},
        )
        response.raise_for_status()
    logger.info("Saved answer for question_id=%s", question_id)


def process_question_message(payload: dict) -> None:
    question_id = payload.get("question_id")
    question_text = payload.get("question_text")
    if question_id is None or not question_text:
        raise ValueError(f"Invalid question payload: {payload}")

    logger.info("Processing question_id=%s", question_id)
    answer_text = generate_answer(question_text)
    save_answer_to_ask_service(int(question_id), answer_text)
