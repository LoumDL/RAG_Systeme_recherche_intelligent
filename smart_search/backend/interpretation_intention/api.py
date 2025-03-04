from fastapi import FastAPI
from pydantic import BaseModel
from main import chatbox

class Qestion(BaseModel):
    question: str

app = FastAPI()

@app.post("/ask")
def prompt(question: Qestion):
    reponse = chatbox(question.question)
    return {"la reponse est": "{}".format(reponse)}

# To run the server, execute the following command:
# uvicorn backend.api.api:app --reload
# Then, go to http://localhost:8