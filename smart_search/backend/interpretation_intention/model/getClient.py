
from qdrant_client import  QdrantClient


def getClient():
    client = QdrantClient(url="http://localhost:6333")
    return client

if __name__ == "__main__":
    print(getClient())  # Devrait maintenant retourner le client mis à jour