from qdrant_client import models, QdrantClient
from sentence_transformers import SentenceTransformer
import numpy as np







def qdrant(documents):
    encoder = SentenceTransformer("all-MiniLM-L6-v2")

    client = QdrantClient(":memory:")  # Remplace par ton endpoint si nécessaire
    collection_name = "my_books"

    # Vérification et création de la collection
    try:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=encoder.get_sentence_embedding_dimension(),
                distance=models.Distance.COSINE,
            ),
        )
    except Exception as e:
        print(f"⚠️ La collection existe déjà ou erreur: {e}")

    # Préparation des points à indexer
    points = []
    for idx, doc in enumerate(documents):
        vector = encoder.encode(str(doc), normalize_embeddings=True)  # Forcer en string et normaliser
        if len(vector.shape) > 1:  # Vérifier si plusieurs vecteurs sont produits
            vector = vector[0]  # Prendre seulement le premier vecteur

        points.append(
            models.PointStruct(
                id=idx, 
                vector=vector.tolist(), 
                payload={"text": doc}  # Stocker en dictionnaire
            )
        )

    client.upload_points(collection_name=collection_name, points=points)

    print(f"✅ {len(documents)} chunks ont été indexés dans Qdrant.")

    return client, encoder  # Retourner le client et l'encodeur pour une réutilisation





def query(client, encoder, question: str):
    hits = client.search(
        collection_name="my_books",
        query_vector=encoder.encode(question).tolist(),
        limit=3,
    )
    
    return hits     


