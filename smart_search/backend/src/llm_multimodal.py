import os
import requests
import base64
from pathlib import Path
import mimetypes








def encode_image_to_data_url(image_path: str) -> str:
    """
    Encode une image en base64 et la convertit en URL de données.
    Prend en charge automatiquement tous les formats d'images reconnus par mimetypes
    (png, jpeg, gif, bmp, etc.).

    :param image_path: Chemin vers l'image à encoder.
    :return: URL de données de l'image.
    :raises FileNotFoundError: Si le fichier image n'existe pas.
    :raises ValueError: Si le fichier n'est pas une image valide.
    """
  
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(f"Le fichier {path} est introuvable.")

    # Deviner le type MIME d'après l'extension du fichier
    mime_type, _ = mimetypes.guess_type(path)
    if not mime_type or not mime_type.startswith("image/"):
        raise ValueError(f"Le fichier {path} n'est pas un format d'image pris en charge.")

    # Lecture et encodage en base64
    raw = path.read_bytes()
    b64_str = base64.b64encode(raw).decode("utf-8")

    return f"data:{mime_type};base64,{b64_str}"




def llm_image(image_path: str , key_openapi:str , question: str = "Qu'y a-t-il dans cette image ?") -> str:
    """
    Fonction principale pour interagir avec l'API multimodale.
    :param image_path: Chemin vers l'image à analyser.
    :return: Réponse de l'API.
    """

    
    # --- Clé API stockée en variable d'environnement (recommandé) ---
    API_KEY = key_openapi or os.getenv("OPENROUTER_API_KEY")
    if not API_KEY:
        raise RuntimeError(
            "Définissez correctement OPENROUTER_API_KEY ou fournissez une vraie clé via key_openapi."
        )






    # --- Préparation de la requête ---
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data_url = encode_image_to_data_url(image_path)

    messages = [
        {
            "role": "user",
            "content": [
                { "type": "text",      "text": question },
                {
                    "type": "image_url",
                    "image_url": { "url": data_url }
                }
            ]
        }
    ]

    payload = {
        "model": "qwen/qwen2.5-vl-3b-instruct:free",
        "messages": messages
    }

    # --- Envoi de la requête ---
    response = requests.post(url, headers=headers, json=payload)
    
    if response.ok:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise RuntimeError(f"Erreur {response.status_code} : {response.text}")







def encode_pdf_to_base64(pdf_path: Path | str) -> str:
    """
    Encode un fichier PDF en une Data URL Base64.

    :param pdf_path: Chemin vers le fichier PDF.
    :return: Chaîne de la forme "data:application/pdf;base64,XXXXX..."
    :raises FileNotFoundError: Si le fichier est introuvable.
    :raises ValueError: Si le fichier n'a pas l'extension .pdf.
    """
    path = Path(pdf_path)
    if not path.is_file():
        raise FileNotFoundError(f"Le fichier {path} est introuvable.")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Le fichier {path} n'est pas un PDF valide.")

    # Lecture binaire et encodage Base64
    raw_bytes = path.read_bytes()
    b64_str = base64.b64encode(raw_bytes).decode("utf-8")

    return f"data:application/pdf;base64,{b64_str}"







def llm_pdf(pdf_path: str, key_openapi: str, question: str = "What are the main points in this document?") -> str:
    """
    Interroge l'API multimodale avec un PDF et renvoie le texte de la réponse.

    :param pdf_path: Chemin vers le fichier PDF à analyser.
    :param key_openapi: Clé API OpenRouter.
    :param question: Question à poser au modèle à propos du PDF.
    :return: Le contenu textuel généré par l'API.
    :raises FileNotFoundError: Si le PDF n'existe pas.
    :raises RuntimeError: Pour toute erreur HTTP ou format inattendu.
    """

    # --- Clé API: soit passée en argument, soit stockée en variable d'environnement ---
    API_KEY = key_openapi or os.getenv("OPENROUTER_API_KEY")
    if not API_KEY:
        raise RuntimeError(
            "Définissez correctement OPENROUTER_API_KEY ou fournissez une vraie clé via key_openapi."
        )

    # Vérification du PDF
    path = Path(pdf_path)
    if not path.is_file():
        raise FileNotFoundError(f"Le fichier {path} est introuvable.")

    # Encode le PDF en Data URL base64 (fonction à définir ou importer)
    data_url = encode_pdf_to_base64(path)

    # Prépare la requête
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": question},
                {
                    "type": "file",
                    "file": {
                        "filename": path.name,
                        "file_data": data_url
                    }
                }
            ]
        }
    ]
    plugins = [
        {"id": "file-parser", "pdf": {"engine": "mistral-ocr"}}
    ]
    payload = {
        "model": "qwen/qwen3-30b-a3b:free",
        "messages": messages,
        "plugins": plugins
    }

    # Envoi et traitement
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
    except requests.HTTPError as e:
        raise RuntimeError(f"Erreur HTTP lors de l'appel API : {e}")
    except ValueError:
        raise RuntimeError("Réponse non JSON de l'API")

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise RuntimeError(f"Format de réponse inattendu : {data}")









if __name__ == "__main__":
    
    key_openapi = "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"  
    pdf_path = "../image/Draft_projet_Hakili_-_ISFAD_v0[1].pdf"  

    try:
        result = llm_pdf(pdf_path, key_openapi, "De quoi parle ce document ?")
        print("Résultat de l'API :", result)
    except Exception as e:
        print("Erreur :", e)
