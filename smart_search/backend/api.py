from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from src.llm import chatbox
from src.db import inserer_chat, modeliserdonnee, set_redis, get_redis
import uvicorn

app = FastAPI()


class Question(BaseModel):
    """
    Modèle de donnée utilisé pour la requête POST dans le point de terminaison /smartsearch.
    """
    question: str


@app.post("/smartsearch/text")
def smart_search_endpoint(payload: Question):
    """
    Endpoint pour interroger le modèle LLM avec une question.
    
    Args:
        payload (Question): Contient une question utilisateur.
        
    Returns:
        dict: Réponse générée par le modèle LLM.
    """
    try:
        # Générer une réponse via le LLM
        reponse_list = chatbox(payload.question)
        reponse = reponse_list[0] if reponse_list else "Aucune réponse trouvée."

        # Modélisation et insertion des données
        donnee = modeliserdonnee(payload.question, reponse)
        cle = set_redis(donnee)
        result_redis = jsonable_encoder(get_redis(cle))
        inserer_chat(result_redis)

        return {"la reponse est": reponse}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")













# Lancement conditionnel du serveur (utile pour le développement local)
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
