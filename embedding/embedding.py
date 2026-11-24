import ollama

EMBEDDING_MODEL = 'hf.co/CompendiumLabs/bge-base-en-v1.5-gguf'
EMBEDDING_DIM = 768

def embed(text):
    return ollama.embed(model=EMBEDDING_MODEL, input=text)['embeddings'][0]