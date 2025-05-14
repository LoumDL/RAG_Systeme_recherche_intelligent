from fastapi import FastAPI, HTTPException, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from src.llm import chatbox
from src.db import inserer_chat, modeliserdonnee, set_redis, get_redis, get_cached_response, set_cached_response
import uvicorn
from typing import Annotated, Optional
from src.llm_multimodal import llm_image, llm_pdf
import tempfile, os, time, json
from pathlib import Path
from dotenv import load_dotenv
import logging
from fastapi.middleware.cors import CORSMiddleware

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)
key_openapi = os.getenv("KEY_OPENAPI")

if not key_openapi:
    logger.warning("KEY_OPENAPI n'est pas définie dans le fichier .env")

# Modèles de données
class Question(BaseModel):
    """
    Modèle de données utilisé pour la requête POST au point de terminaison /smartsearch/text.
    """
    question: str

class ResponseModel(BaseModel):
    """
    Modèle de données pour la réponse standardisée de l'API.
    """
    reponse: str
    status: str = "success"
    processing_time: float

# Création de l'application FastAPI
app = FastAPI(
    title="Smart Search API",
    description="API pour la recherche intelligente de textes et l'analyse multimodale",
    version="1.0.0"
)

# Configuration CORS pour permettre les requêtes cross-origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À remplacer par les origines spécifiques en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supprimé car maintenant importé de src.db

def log_to_history(background_tasks: BackgroundTasks, question: str, reponse: str):
    """
    Enregistre l'historique de manière asynchrone pour ne pas bloquer la réponse API
    """
    def _log():
        try:
            donnee = modeliserdonnee(question, reponse)
            cle = set_redis(donnee)
            result_redis = jsonable_encoder(get_redis(cle))
            inserer_chat(result_redis)
            logger.info(f"Historique enregistré pour la question: {question[:30]}...")
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de l'historique: {str(e)}")
    
    background_tasks.add_task(_log)

@app.post("/smartsearch/text", response_model=ResponseModel)
async def smart_search_endpoint(
    payload: Question, 
    background_tasks: BackgroundTasks
):
    """
    Endpoint pour interroger le modèle LLM avec une question textuelle.
   
    Args:
        payload (Question): Contient la question de l'utilisateur.
        background_tasks: Tâches à exécuter en arrière-plan.
       
    Returns:
        dict: Réponse générée par le modèle LLM avec le temps de traitement.
    """
    start_time = time.time()
    question = payload.question.strip()
    
    if not question:
        return JSONResponse(
            status_code=400, 
            content={"status": "error", "reponse": "La question ne peut pas être vide"}
        )
    
    # Vérifier le cache
    cached_response = get_cached_response(question)
    if cached_response:
        processing_time = time.time() - start_time
        log_to_history(background_tasks, question, cached_response)
        return {"reponse": cached_response, "processing_time": processing_time}
    
    try:
        # Générer une réponse via le LLM
        reponse_list = chatbox(question)
        
        if not reponse_list:
            raise HTTPException(status_code=500, detail="Le modèle n'a pas retourné de réponse")
            
        # Joindre les éléments de la liste en une seule chaîne
        reponse = " ".join(reponse_list)
        
        # Mettre en cache la réponse pour les futures requêtes
        set_cached_response(question, reponse)
        
        # Enregistrer l'historique en arrière-plan
        log_to_history(background_tasks, question, reponse)
        
        # Calculer le temps de traitement
        processing_time = time.time() - start_time
        
        return {
            "reponse": reponse, 
            "status": "success", 
            "processing_time": processing_time
        }
   
    except Exception as e:
        logger.error(f"Erreur lors du traitement de la requête: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@app.post("/smartsearch/multimodal", response_model=ResponseModel)
async def multimodal_search(
    background_tasks: BackgroundTasks,
    prompt: Annotated[str, Form()],
    file: Annotated[UploadFile, File()]
) -> dict:
    """
    Endpoint pour traiter une image ou un PDF avec une requête multimodale.
    
    Args:
        background_tasks: Tâches à exécuter en arrière-plan.
        prompt: Texte de la question ou instruction pour le traitement du fichier.
        file: Fichier image ou PDF à analyser.
        
    Returns:
        dict: Réponse générée par le modèle avec le temps de traitement.
    """
    start_time = time.time()
    
    if not prompt.strip():
        return JSONResponse(
            status_code=400, 
            content={"status": "error", "reponse": "Le prompt ne peut pas être vide"}
        )
    
    if not file:
        return JSONResponse(
            status_code=400, 
            content={"status": "error", "reponse": "Aucun fichier n'a été fourni"}
        )
    
    # Tenter de récupérer du cache pour les requêtes multimodales
    cache_key = f"{prompt}_{file.filename}"
    cached_response = get_cached_response(cache_key)
    if cached_response:
        processing_time = time.time() - start_time
        return {
            "reponse": cached_response,
            "status": "success",
            "processing_time": processing_time,
            "source": "cache"
        }
    
    content_type = file.content_type
    supported_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    
    if content_type not in supported_types:
        return JSONResponse(
            status_code=400, 
            content={"status": "error", "reponse": f"Type de fichier non supporté: {content_type}. Types supportés: {', '.join(supported_types)}"}
        )
    
    if not key_openapi:
        return JSONResponse(
            status_code=500, 
            content={"status": "error", "reponse": "Clé API non configurée sur le serveur"}
        )
    
    try:
        # Lecture du fichier en mémoire
        contents = await file.read()
        
        # Création d'un fichier temporaire avec la bonne extension
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(contents)
            tmp.flush()
            tmp_path = tmp.name
            
        try:
            # Traitement selon le type de fichier
            if content_type in ("image/jpeg", "image/png", "image/jpg"):
                reponse = llm_image(tmp_path, key_openapi, prompt)
            elif content_type == "application/pdf":
                reponse = llm_pdf(tmp_path, key_openapi, prompt)
            
            # Enregistrement dans l'historique en arrière-plan
            log_to_history(background_tasks, f"[Multimodal] {prompt}", reponse)
            
            # Mettre en cache la réponse pour les futures requêtes (avec le nom du fichier comme partie de la clé)
            cache_key = f"{prompt}_{file.filename}"
            set_cached_response(cache_key, reponse)
            
            # Calculer le temps de traitement
            processing_time = time.time() - start_time
            
            return {
                "reponse": reponse,
                "status": "success",
                "processing_time": processing_time
            }
            
        finally:
            # Nettoyage du fichier temporaire
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
                
    except Exception as e:
        logger.error(f"Erreur lors du traitement multimodal: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur de traitement: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Événements à exécuter au démarrage du serveur"""
    logger.info("Démarrage de l'API Smart Search")
    from src.db import initialize_databases
    status = initialize_databases()
    
    # Vérifier que toutes les bases de données sont disponibles
    all_ok = all(status.values())
    if all_ok:
        logger.info("✅ Toutes les bases de données sont disponibles")
    else:
        logger.warning("⚠️ Certaines bases de données ne sont pas disponibles - Vérifiez les logs")

@app.on_event("shutdown")
async def shutdown_event():
    """Événements à exécuter à l'arrêt du serveur"""
    logger.info("Arrêt de l'API Smart Search")

# Lancement conditionnel du serveur (utile pour le développement local)
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)