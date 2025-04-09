from fastapi import FastAPI
from pydantic import BaseModel
from src.llm import chatbox 
from src.db import inserer_chat , modeliserdonnee
import uvicorn

# Définition du modèle de la question (utilisé pour la validation des données entrantes)
class Question(BaseModel):
    """
    Modèle de donnée utilisé pour la requête POST dans le point de terminaison /llm.
    
    Attributs:
        question (str): La question à poser au modèle LLM pour générer une réponse.
    """
    question: str

# Création de l'instance FastAPI
app = FastAPI()

@app.post("/smartsearch")
def prompt(question: Question):
    """
    Point de terminaison pour obtenir une réponse à une question via un modèle LLM.
    
    Cette fonction prend une question en entrée, la transmet au modèle LLM via la fonction 
    `chatbox` et retourne la réponse générée.
    
    Args:
        question (Question): Un objet contenant une chaîne de caractères représentant la question.
        
    Returns:
        dict: Un dictionnaire contenant la réponse générée par le modèle LLM sous la forme d'un message.
        
    Exemple de réponse:
        {
            "la reponse est": "Voici la réponse à votre question."
        }
    """
    
    reponse = chatbox(question.question)  # Appelle la fonction chatbox pour obtenir la réponse à la question
    reponse = reponse[0] if reponse else "Aucune réponse trouvée."  # Vérifie si une réponse a été obtenue

    # Modélise les données à insérer dans la base de données
    donnee = modeliserdonnee(question.question, reponse)
    # Insère les données dans la base de données
    inserer_chat(donnee)

    return {"la reponse est": "{}".format(reponse)}  # Retourne la réponse générée sous forme de dictionnaire


# Parameters
SERVER_ADDR = "0.0.0.0"
SERVER_PORT = 8000


if __name__ == "__main__":
    uvicorn.run(app, host=SERVER_ADDR, port=SERVER_PORT)






# To run the server, execute the following command:
# uvicorn backend.api.api:app --reload
# Then, go to http://localhost:8000

# To run the server with the specified host and port:
# uvicorn api:app --host 0.0.0.0 --port 8000 --reload