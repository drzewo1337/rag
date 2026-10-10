from rag_service.cosine_sim import cosine_similarity
import ollama
from rag_service.embedding import EMBEDDING_MODEL

def read_facts_from_database(): #connect to postgres database and read facts from database
  return [("Fact 1", [0.1, 0.2, 0.3]), ("Fact 2", [0.4, 0.5, 0.6]), ("Fact 3", [0.7, 0.8, 0.9])]

def retrieve(query, top_n=3): 
  query_embedding = ollama.embed(model=EMBEDDING_MODEL, input=query)['embeddings'][0]
  # temporary list to store (chunk, similarity) pairs
  similarities = []
  for chunk, embedding in read_facts_from_database():
    similarity = cosine_similarity(query_embedding, embedding)
    similarities.append((chunk, similarity))
  # sort by similarity in descending order, because higher similarity means more relevant chunks
  similarities.sort(key=lambda x: x[1], reverse=True)
  # finally, return the top N most relevant chunks
  return similarities[:top_n]