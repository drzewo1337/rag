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
                SELECT d.filename, c.page, c.content,
                       1 - (c.embedding <=> CAST(:embedding AS vector)) AS similarity
                FROM chunks c
                JOIN documents d ON d.id = c.document_id
                WHERE c.embedding IS NOT NULL
                ORDER BY c.embedding <=> CAST(:embedding AS vector)
                LIMIT :top_n
                """
            ),
            {"embedding": str(query_embedding), "top_n": top_n},
        ).fetchall()
    return [
        (f"[{filename}, p. {page}] {content}", float(similarity))
        for filename, page, content, similarity in rows
    ]
