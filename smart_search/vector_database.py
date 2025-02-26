from qdrant_client import models, QdrantClient
from sentence_transformers import SentenceTransformer
import numpy as np






def insert_documents_into_qdrant(documents):
    collection_name="my_books"
    encoder = SentenceTransformer("Alibaba-NLP/gte-Qwen2-7B-instruct", trust_remote_code=True) # all-MiniLM-L6-v2          #"Alibaba-NLP/gte-Qwen2-7B-instruct", trust_remote_code=True
    client = QdrantClient(":memory:")  # Remplace par ton endpoint si nécessaire

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

    # Insertion des points dans la base de données
    client.upload_points(collection_name=collection_name, points=points)

    print(f"✅ {len(documents)} documents ont été indexés dans Qdrant.")
    return client  # Retourne le client pour utilisation dans les requêtes






def query_qdrant( query_text,client):

    
    collection_name="my_books"
    top_k=1

    encoder = SentenceTransformer("Alibaba-NLP/gte-Qwen2-7B-instruct", trust_remote_code=True)
    
    # Conversion de la requête en vecteur
    query_vector = encoder.encode(query_text, normalize_embeddings=True)
    
    # Effectuer la recherche dans Qdrant
    results = client.search(
        collection_name=collection_name,
        query_vector=query_vector.tolist(),
        limit=top_k  # Nombre de résultats à retourner
    )
    
    #return results

    res = []
    
    # Affichage des résultats
    for result in results:
        #print(f"ID: {result.id}, Score: {result.score}, Text: {result.payload['text']}")

        res.append(result.payload['text'])
    return res




