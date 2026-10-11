import ast
import os

from sqlalchemy import create_engine, text


def read_facts_from_database() -> list[tuple[str, list[float]]]:
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@database:5432/rag_service_db",
    )
    engine = create_engine(database_url)
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT fact_text, embedding FROM facts")).fetchall()

    facts: list[tuple[str, list[float]]] = []
    for fact_text, embedding_raw in rows:
        if embedding_raw is None:
            continue
        embedding = ast.literal_eval(embedding_raw)
        facts.append((fact_text, embedding))
    return facts
