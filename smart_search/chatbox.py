from llm import llm
from load_the_database import load_the_database





question = str(input("Entrez votre question: "))
client = load_the_database()
resultats = llm(question, client)
print(resultats)