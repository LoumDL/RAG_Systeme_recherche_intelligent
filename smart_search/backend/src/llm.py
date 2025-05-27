import requests
from langdetect import detect
from .db import query_qdrant, modeliserdonnee, inserer_chat, get_cached_response, set_cached_response
import logging
import re

# Configuration du logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paramètres de l'API Ollama
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen3"  #alternative on utilise qwen3 || qwen3:30b-a3b || qwen3:7b-a3b
MAX_TOKENS = 512  # Augmenté pour des réponses plus complètes

def llm(question: str) -> list[str]:
    """
    Interroge un modèle LLM (qwen3) avec une question et des données récupérées depuis Qdrant.

    Args:
        question (str): La question posée par l'utilisateur.
   
    Returns:
        list[str]: Une liste de phrases extraites de la réponse du modèle.
    """
    try:
        # 1) Recherche de contexte dans Qdrant
        resultats = query_qdrant(question)
        
        # Gestion des résultats vides ou malformés de Qdrant
        if not resultats:
            logger.warning("Aucun résultat trouvé dans Qdrant pour la question: %s", question)
            contexte = ""
        else:
            # Supposons que query_qdrant retourne déjà les textes et non des tuples
            contexte = resultats[0] if isinstance(resultats[0], str) else str(resultats[0])
        
        # 2) Construction du prompt enrichi
        prompt = (
            "Vous êtes un assistant francophone compétent qui fournit des réponses précises.  Réponds exclusivement en français\n\n"
            f"Contexte: {contexte}\n\n"
            f"Question: {question}\n"
            "Réponse:"
        )
        
        # 3) Appel à l'API Ollama avec timeout
        resp = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "max_tokens": MAX_TOKENS,
                "temperature": 0.7,  # Ajout d'un paramètre de température pour contrôler la créativité
            },
            #timeout=30  # Timeout pour éviter les blocages
        )
        
        # Vérification de la réponse HTTP
        resp.raise_for_status()
        data = resp.json()
        
        # 4) Extraction et normalisation de la réponse
        reponse = data.get("response", "")
        reponse = re.sub(r'<think>.*?</think>', '', reponse, flags=re.DOTALL)
        reponse = re.sub(r'\n+', '\n', reponse.strip())
        
        
        if not reponse:
            logger.warning("Réponse vide reçue du modèle")
            return ["Désolé, je n'ai pas pu générer de réponse pertinente."]
            
        # Segmentation de la réponse en phrases
        if isinstance(reponse, str):
            # Filtrage des lignes vides
            lignes = [l.strip() for l in reponse.splitlines() if l.strip()]
            return lignes if lignes else [reponse]
        elif isinstance(reponse, list):
            return reponse
        else:
            return [str(reponse)]
            
    except requests.exceptions.RequestException as e:
        logger.error("Erreur lors de la requête à Ollama: %s", str(e))
        return ["Désolé, le service de réponse est temporairement indisponible."]
    except Exception as e:
        logger.error("Erreur inattendue: %s", str(e))
        return ["Une erreur s'est produite lors du traitement de votre question."]



def chatbox(question: str) -> list[str]:
    """
    Fonction de chat qui utilise le LLM pour répondre à une question.
   
    Args:
        question (str): La question posée par l'utilisateur.
   
    Returns:
        list: Liste des réponses du modèle.
    """
    try:
        # Vérification que la question n'est pas vide
        if not question or not question.strip():
            return ["Veuillez poser une question."]
            
        # Obtention des résultats du LLM
        resultats = llm(question)
        
        # Enregistrement du dialogue pour référence future
        if resultats and len(resultats) > 0:
            try:
                reponse = ' '.join(resultats)
                donnee = modeliserdonnee(question, reponse)
                inserer_chat(donnee)
            except Exception as e:
                logger.error("Erreur lors de l'enregistrement de l'historique: %s", str(e))
                
        return resultats
        
    except Exception as e:
        logger.error("Erreur dans chatbox: %s", str(e))
        return [f"Une erreur est survenue: {str(e)}"]




if __name__ == "__main__":
    question = input("Posez votre question: ")
    resl = chatbox(question)
    print('\n'.join(resl))