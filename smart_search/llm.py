import ollama
from load_the_database import load_the_database
from vector_database import query_qdrant

client = load_the_database()

question = "quel est le role de l'expert fiscale ?"
resultats = query_qdrant(question, client)

# Aplatir la liste de listes en une liste simple
resultats_aplati = [item for sublist in resultats for item in sublist]

# Convertir la liste aplatie en une chaîne de caractères
res = " ".join(resultats_aplati)

print(res)