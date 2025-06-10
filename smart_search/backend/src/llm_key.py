import requests
import json
import logging
from .db import query_qdrant
from pathlib import Path
from dotenv import load_dotenv
import os

# Configuration du logger (à définir si pas déjà fait)
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)
key_openapi = os.getenv("KEY_OPENAPI")

def llm_text(question: str) -> str:
    """
    Envoie une question à l'API OpenRouter pour obtenir une réponse du modèle Qwen3.
    Args:
        question (str): La question à poser au modèle.
        
    Returns:
        str: La réponse du modèle.
    """
    if not question or not question.strip():
        return "Veuillez fournir une question valide."
    
    # 1) Recherche de contexte dans Qdrant
    try:
        resultats = query_qdrant(question)
        
        # Gestion des résultats vides ou malformés de Qdrant
        if not resultats:
            logger.warning("Aucun résultat trouvé dans Qdrant pour la question: %s", question)
            contexte = ""
        else:
            # Supposons que query_qdrant retourne déjà les textes et non des tuples
            contexte = resultats[0] if isinstance(resultats[0], str) else str(resultats[0])
    except Exception as e:
        logger.error("Erreur lors de la recherche dans Qdrant: %s", e)
        contexte = ""
    
    # 2) Construction du prompt enrichi
    prompt = (
        "Vous êtes un assistant francophone compétent qui fournit des réponses précises. Réponds exclusivement en français\n\n"
        f"Contexte: {contexte}\n\n"
        f"Question: {question}\n"
        "Réponse:"
    )
    
    # 3) Préparation de la requête
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {key_openapi}",
                "Content-Type": "application/json"  
            },
            data=json.dumps({
                "model": "deepseek/deepseek-r1-0528:free",
                "messages": [
                    {
                        "role": "user",
                        "content": "Repondez exclusivement en francais : " + prompt
                    }
                ],
            })
        )
        
        # Vérification du statut de la réponse
        response.raise_for_status()
        
        # Extraction de la réponse
        data = response.json()
        return data["choices"][0]["message"]["content"]
        
    except requests.HTTPError as e:
        logger.error("Erreur HTTP lors de l'appel API : %s", e)
        return f"Erreur lors de la requête à l'API : {e}"
    except KeyError as e:
        logger.error("Format de réponse inattendu : %s", e)
        return "Erreur : format de réponse inattendu de l'API"
    except Exception as e:
        logger.error("Erreur inattendue : %s", e)
        return f"Erreur inattendue : {e}"


