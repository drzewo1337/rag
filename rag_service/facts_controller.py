from fastapi import FastAPI
from pydantic import BaseModel

class Fact(BaseModel):
    fact: str

app = FastAPI()

facts = []

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/facts")
def read_facts():
    return {"facts": facts}

@app.put("/fact")
def put_fact(fact: Fact):
    facts.append(fact.fact)
    return {"message": "Fact added successfully"}