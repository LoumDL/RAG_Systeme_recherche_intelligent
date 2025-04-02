from qdrant_client import models, QdrantClient
from sentence_transformers import SentenceTransformer
from .texte import (extraction_markdown, markdown_file, Chunker)
from pathlib import Path
import os

# Initialisation du client Qdrant et de l'encodeur
client = QdrantClient(url="http://localhost:6333")
encoder = SentenceTransformer("Alibaba-NLP/gte-Qwen2-1.5B-instruct", trust_remote_code=True)
collection_name = "smart_search"

def initialize_collection():
    """
    Initialise la collection Qdrant si elle n'existe pas.
    
    Si la collection existe déjà, une erreur est capturée et affichée.
    """
    try:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=1536,  # Taille du vecteur attendu par le modèle
                distance=models.Distance.COSINE,
            ),
        )
        print(f" Collection '{collection_name}' créée.")
    except Exception as e:
        print(f" La collection existe déjà ou erreur: {e}")

def insert_documents_into_qdrant(documents):
    """
    Insère une liste de documents vectorisés dans la base de données Qdrant.
    
    Args:
        documents (list): Liste des documents sous forme de texte.
    """
    points = [
        models.PointStruct(
            id=idx, 
            vector=encoder.encode(str(doc)).tolist(),  # Encodage du document en vecteur
            payload={"text": doc}  # Stockage du texte original
        )
        for idx, doc in enumerate(documents)
    ]

    client.upload_points(collection_name=collection_name, points=points)
    print(f"{len(documents)} documents ont été indexés dans Qdrant.")

def query_qdrant(query_text):
    """
    Recherche un document similaire à la requête donnée en utilisant la similarité cosinus.
    
    Args:
        query_text (str): Texte de la requête.
    
    Returns:
        list: Liste contenant le texte du document le plus pertinent trouvé.
    """
    top_k = 1  # Nombre de résultats à retourner
    query_vector = encoder.encode(query_text)

    results = client.search(
        collection_name=collection_name,
        query_vector=query_vector.tolist(),
        limit=top_k
    )

    return [result.payload['text'] for result in results]

def load_the_database():
    """
    Charge les fichiers PDF, extrait leur contenu en Markdown, segmente le texte en chunks et les insère dans Qdrant.
    """
    chemin_dossier = Path("/home/ubuntu/Hakili/RAG_Systeme_recherche_intelligent/smart_search/backend/data")
    fichiers_pdf = list(chemin_dossier.rglob("*.pdf"))  

    if not fichiers_pdf:
        print("Aucun fichier PDF trouvé.")
        return None

    dossier_markdown = Path("../markdown_files")
    dossier_markdown.mkdir(parents=True, exist_ok=True)

    for i, file_path in enumerate(fichiers_pdf):
        markdown = extraction_markdown(str(file_path))
        fichier_markdown = dossier_markdown / f"fichier{i}.md"
        markdown_file(markdown, fichier_markdown)

        if not fichier_markdown.exists():
            print(f"Erreur : {fichier_markdown} n'a pas été créé.")
            continue

        chunks = Chunker(str(fichier_markdown))
        insert_documents_into_qdrant(chunks)

if __name__ == "__main__":
    initialize_collection()
    load_the_database()
    print("Database loaded successfully")
