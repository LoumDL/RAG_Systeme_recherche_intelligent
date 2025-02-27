#from llm import llm
from backend.interpretation_intention.model.llm import llm
#from load_the_database import getClient, load_the_database
from backend.interpretation_intention.bd_qdrant.load_the_database import getClient, load_the_database




def chatbox(question: str):
    load_the_database()  # Charger la base de données (si nécessaire)
    client = getClient()  # Récupérer le client mis à jour
    if client is None:
        print("Erreur : Client non initialisé.")
        return
    
    resultats = llm(question, client)
    print(resultats)




if __name__ == "__main__":
    question = input("Posez votre question :  ")
    chatbox(question)
