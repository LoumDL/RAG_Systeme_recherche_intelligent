# Description: Ce fichier permet de charger les fichiers PDF dans la base de données Qdrant.
from traitement.word_processing_function import (
    extraction_markdown, markdown_file, Chunker
)

from bd_qdrant.vector_database import insert_documents_into_qdrant, query_qdrant, initialize_collection
from pathlib import Path
import os


initialize_collection()


def load_the_database():
     

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

        insert_documents_into_qdrant(chunks)  # Mise à jour de la variable globale






if __name__ == "__main__":
    load_the_database()
    print("Database loaded successfully")

    #print(getClient())  # Devrait maintenant retourner le client mis à jour
