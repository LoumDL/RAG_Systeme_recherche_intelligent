from backend.main import chatbox
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Définition du modèle pour la requête
class QuestionRequest(BaseModel):
    question: str

@app.get("/ask/")
async def ask_question(request: QuestionRequest):
    reponse = chatbox(request.question)
    return {"question": request.question, "reponse": reponse}
