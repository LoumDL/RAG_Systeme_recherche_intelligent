# load_the_database.py
from word_processing_function import extraction_markdown, markdown_file, Chunker
from vector_database import insert_documents_into_qdrant, query_qdrant
from pathlib import Path
import os

client = None  # Variable globale

def load_the_database():
    global client  # Permet de modifier la variable globale

    # Récupérer les fichiers PDF
    chemin_dossier = Path("/home/dame/djibyloum/RAG_Hakili/RAG_Systeme_recherche_intelligent/isfad_courses") 
    fichiers_pdf = list(chemin_dossier.rglob("*.pdf"))  

    if not fichiers_pdf:
        print("Aucun fichier PDF trouvé.")
        return None

    for i, file_path in enumerate(fichiers_pdf):
        markdown = extraction_markdown(str(file_path))
        markdown_file(markdown, i)

        fichier_markdown = f"./fichier{i}.md"
        if not os.path.exists(fichier_markdown):
            print(f"Erreur : {fichier_markdown} n'a pas été créé.")
            continue

        chunks = Chunker(fichier_markdown)
        client = insert_documents_into_qdrant(chunks)  # Mise à jour de la variable globale

def getClient():
    return client 

if __name__ == "__main__":
    load_the_database()
    print("Database loaded successfully")

    #print(getClient())  # Devrait maintenant retourner le client mis à jour
