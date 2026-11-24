import json
import logging
import os
import re

import httpx
import ollama

from rag_service.retrieve import retrieve


logger = logging.getLogger(__name__)


LANGUAGE_MODEL = "hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF"
_CITE = re.compile(r"\[(\d+)\](?!\()")
_CODE = re.compile(r"```.*?```|`[^`]*`", re.DOTALL)


def cited_source_ids(answer: str, known_ids: set[int]) -> list[int]:
    visible = _CODE.sub("", answer)
    found: list[int] = []
    seen: set[int] = set()
    for match in _CITE.finditer(visible):
        source_id = int(match.group(1))
        if source_id not in known_ids or source_id in seen:
            continue
        seen.add(source_id)
        found.append(source_id)
    return found


def generate_answer(question_text: str) -> dict:
    rows = retrieve(question_text)
    sources = [
        {
            "id": index,
            "filename": row["filename"],
            "page": row["page"],
            "content": row["content"],
        }
        for index, row in enumerate(rows, start=1)
    ]
    context = "\n\n".join(
        f"[{source['id']}] {source['filename']}, page {source['page']}\n{source['content']}"
        for source in sources
    ) or "(no context)"
    instruction_prompt = f"""You are a helpful chatbot.
Use only the context to answer. Do not make up information.
Write the answer in Markdown.
When you use a context item, cite it as [1] or [2]. Cite only items you use.

Context:
{context}
"""
    response = ollama.chat(
        model=LANGUAGE_MODEL,
        messages=[
            {"role": "system", "content": instruction_prompt},
            {"role": "user", "content": question_text},
        ],
    )
    answer = response["message"]["content"]
    known_ids = {source["id"] for source in sources}
    used_ids = set(cited_source_ids(answer, known_ids))
    return {
        "answer": answer,
        "sources": [source for source in sources if source["id"] in used_ids],
    }


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
    answer = generate_answer(question_text)
    save_answer_to_ask_service(int(question_id), json.dumps(answer, ensure_ascii=False))
