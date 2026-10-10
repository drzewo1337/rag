import ollama
from fastapi import FastAPI
from rag_service.retrieve import retrieve


LANGUAGE_MODEL = 'hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF'


app = FastAPI()


@app.get("/health")
async def health_check():
  return {"status": "ok"}


@app.post("/answer")
async def answer(query: str):
  retrieved_knowledge = retrieve(query)
  return {"answer": retrieved_knowledge}


input_query = "How many legs does cat have?"
retrieved_knowledge = retrieve(input_query)


print('Retrieved knowledge:')
for chunk, similarity in retrieved_knowledge:
  print(f' - (similarity: {similarity:.2f}) {chunk}')


instruction_prompt = f'''You are a helpful chatbot.
Use only the following pieces of context to answer the question. Don't make up any new information:
{'\n'.join([f' - {chunk}' for chunk, similarity in retrieved_knowledge])}
'''


stream = ollama.chat(
  model=LANGUAGE_MODEL,
  messages=[
    {'role': 'system', 'content': instruction_prompt},
    {'role': 'user', 'content': input_query},
  ],
  stream=True,
)


# print the response from the chatbot in real-time
print('Chatbot response:')
for chunk in stream:
  print(chunk['message']['content'], end='', flush=True)
