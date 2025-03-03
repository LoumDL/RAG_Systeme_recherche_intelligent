from qdrant_client import models, QdrantClient
from sentence_transformers import SentenceTransformer



# Initialisation du client Qdrant et de l'encodeur
client = QdrantClient(url="http://localhost:6333")
encoder = SentenceTransformer("Alibaba-NLP/gte-Qwen2-7B-instruct", trust_remote_code=True)       #Alibaba-NLP/gte-Qwen2-7B-instruct", trust_remote_code=True |all-MiniLM-L6-v2
collection_name = "smart_search"



def initialize_collection():
    # Création de la collection si elle n'existe pas
    
    try:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=384,           #encoder.get_sentence_embedding_dimension(),
                distance=models.Distance.COSINE,
            ),
        )
        print(f" Collection '{collection_name}' créée.")
    except Exception as e:
        print(f" La collection existe déjà ou erreur: {e}")
    
    
    """
    try:
        client.delete_collection(collection_name)
        print(f" Collection '{collection_name}' supprimée.")
    except Exception as e:
        print(f" La collection n'existe pas ou erreur: {e}")
    """



def insert_documents_into_qdrant(documents):
    # Préparation des points à indexer
    points = [
        models.PointStruct(
            id=idx, 
            vector=encoder.encode(str(doc)).tolist(),  # Encodage du document
            payload={"text": doc}  # Stockage du texte original
        )
        for idx, doc in enumerate(documents)
    ]

    # Insertion des points dans la collection
    client.upload_points(collection_name=collection_name, points=points)

    print(f"{len(documents)} documents ont été indexés dans Qdrant.")






def query_qdrant(query_text):
    top_k = 1  # Nombre de résultats à retourner

    # Encodage de la requête en vecteur
    query_vector = encoder.encode(query_text)

    # Recherche dans la collection
    results = client.search(
        collection_name=collection_name,
        query_vector=query_vector.tolist(),
        limit=top_k
    )

    # Extraction et retour des résultats
    return [result.payload['text'] for result in results]




