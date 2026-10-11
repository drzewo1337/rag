from rag_service.cosine_sim import cosine_similarity
from embedding.embedding import embed
from rag_service.facts_reader import read_facts_from_database


def retrieve(query: str, top_n: int = 3) -> list[tuple[str, float]]:
    query_embedding = embed(query)
    similarities: list[tuple[str, float]] = []
    for chunk, embedding in read_facts_from_database():
        similarity = cosine_similarity(query_embedding, embedding)
        similarities.append((chunk, similarity))
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_n]
