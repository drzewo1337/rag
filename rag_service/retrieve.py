import os

from sqlalchemy import create_engine, text

from embedding.embedding import embed


def retrieve(query: str, top_n: int = 3) -> list[dict]:
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
                SELECT d.filename, c.page, c.content
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
        {"filename": filename, "page": int(page), "content": content}
        for filename, page, content in rows
    ]
