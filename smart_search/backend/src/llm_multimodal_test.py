import requests
import base64
from pathlib import Path
import requests
import fitz  # PyMuPDF
import tiktoken
from .texte import extraction_markdown
from IPython.display import Markdown



def llm_image(image_path, question="Qu'y a-t-il dans cette image ?"):
    """
    Analyse une image avec le modèle llama3.2-vision via Ollama.
    
    Args:
        image_path: Chemin vers l'image à analyser
        question: Question à poser au modèle concernant l'image
        
    Returns:
        Réponse textuelle du modèle
    """
    question = question + " Répondez exclusivement en français."
    # Vérifier que le fichier existe
    path = Path(image_path)
    if not path.exists():
        return f"Erreur: Le fichier {image_path} n'existe pas"
        
    # Encoder l'image en base64
    with open(image_path, "rb") as img_file:
        base64_image = base64.b64encode(img_file.read()).decode("utf-8")
    
    # Préparer la requête pour Ollama
    ollama_url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3.2-vision:latest",
        "prompt": question,
        "images": [base64_image],
        "stream": False,
        "max_tokens": 500
    }
    
    # Envoyer la requête
    try:
        response = requests.post(ollama_url, json=payload)
        response.raise_for_status()  # Lever une exception si la requête échoue
        
        # Extraire la réponse
        result = response.json().get("response", "")
        return result
    except Exception as e:
        return f"Erreur lors de l'analyse: {str(e)}"






def llm_pdf(pdf_path, question="De quoi parle ce document ?"):
    """
    Extrait tout le texte d'un PDF, le tronque si trop long pour le modèle, 
    et l'envoie à Ollama avec une question.

    """
    try:
        markdown = extraction_markdown(pdf_path)
        text_content = markdown.markdown

        # Préparer prompt
        contexte = f"Contenu du document PDF:\n{text_content}"
        prompt = (
            "Vous êtes un assistant compétent qui fournit des réponses précises.\n\n"
            f"Contexte: {contexte}\n\n"
            f"Question: {question}\n"
            "Réponse:"
        )

        # Envoyer à Ollama
        ollama_url = "http://localhost:11434/api/generate"
        payload = {
            "model": "qwen3",
            "prompt": prompt,
            "stream": False,
            "max_tokens": 500,
            "temperature": 0.7
        }

        print("Envoi de la requête à Ollama...")
        response = requests.post(ollama_url, json=payload)
        response.raise_for_status()

        return response.json().get("response", "")

    except Exception as e:
        return f"Erreur lors de l'analyse du PDF: {str(e)}"










# Exemple d'utilisation
if __name__ == "__main__":
    
    """
    # Remplacez par le chemin de votre image
    image_path = "./image/Dockerfile1.png"
    
    # Analyser l'image
    reponse = llm_image(image_path, "Décrivez cette image en détail. Repondes exclusivement en francais")
    
    # Afficher le résultat
    print(reponse)
    """
     # Remplacez par le chemin de votre PDF
    pdf_path = "./image/Draft_projet_Hakili_-_ISFAD_v0[1].pdf"
    
    # Analyser le PDF
    reponse = llm_pdf(pdf_path, "Résumez le contenu de ce document.Repondes exclusivement en francais")
    
    # Afficher le résultat
    print(reponse)