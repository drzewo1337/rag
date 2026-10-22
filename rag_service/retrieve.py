import os

from sqlalchemy import create_engine, text

from embedding.embedding import embed


def retrieve(query: str, top_n: int = 3) -> list[tuple[str, float]]:
    query_embedding = embed(query)
    database_url = os.getenv(
        "DATABASE_URL",
    )
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
        
    engine = create_engine(database_url)
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT fact_text,
                       1 - (embedding <=> CAST(:embedding AS vector)) AS similarity
                FROM facts
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> CAST(:embedding AS vector)
                LIMIT :top_n
                """
            ),
            {"embedding": str(query_embedding), "top_n": top_n},
        ).fetchall()
    return [(fact_text, float(similarity)) for fact_text, similarity in rows]
