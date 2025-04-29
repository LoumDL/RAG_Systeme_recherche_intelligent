from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from src.llm import chatbox
from src.db import inserer_chat, modeliserdonnee, set_redis, get_redis
import uvicorn
from typing import Annotated
from src.llm_multimodal import llm_image, llm_pdf
import tempfile, os
from pathlib import Path


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









@app.post("/smartsearch/multimodal")
async def multimodal_search(prompt: Annotated[str, Form()],file: Annotated[UploadFile, File()]) -> dict:
    
    """
    Route FastAPI pour traiter une image ou un PDF envoyé en multipart/form-data :
      - sauvegarde le fichier dans un fichier temporaire
      - appelle llm_image ou llm_pdf selon le content_type
      - nettoie le fichier temporaire
    """

    key_openapi = "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"


    content_type = file.content_type
    # Lecture du fichier en mémoire
    contents = await file.read()
    # Création d'un fichier temporaire avec la bonne extension ,et je suis bloquer sur git
    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(contents)
        tmp.flush()
        tmp_path = tmp.name

    try:
        if content_type in ("image/jpeg", "image/png", "image/jpg"):
            reponse = llm_image(tmp_path, key_openapi, prompt)
        elif content_type == "application/pdf":
            reponse = llm_pdf(tmp_path, key_openapi, prompt)
        else:
            raise HTTPException(status_code=400, detail="Type de fichier non pris en charge.")
    finally:
        os.remove(tmp_path)

    return {"la reponse est": reponse}









# Lancement conditionnel du serveur (utile pour le développement local)
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
