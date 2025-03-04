from traitement.word_processing_function import (
    extraction_markdown, markdown_file, Chunker
)

from bd_qdrant.vector_database import insert_documents_into_qdrant, query_qdrant, initialize_collection
from pathlib import Path
import os

initialize_collection()

def load_the_database():
    # Dossier contenant les fichiers PDF
    chemin_dossier = Path("/home/dame/djibyloum/RAG_Hakili/RAG_Systeme_recherche_intelligent/isfad_courses") 
    fichiers_pdf = list(chemin_dossier.rglob("*.pdf"))  

    if not fichiers_pdf:
        print("Aucun fichier PDF trouvé.")
        return None

    # Dossier pour stocker les fichiers Markdown
    dossier_markdown = Path("./markdown_files")
    dossier_markdown.mkdir(parents=True, exist_ok=True)  # Création du dossier s'il n'existe pas

    for i, file_path in enumerate(fichiers_pdf):
        markdown = extraction_markdown(str(file_path))
        
        fichier_markdown = dossier_markdown / f"fichier{i}.md"
        markdown_file(markdown, fichier_markdown)

        if not fichier_markdown.exists():
            print(f"Erreur : {fichier_markdown} n'a pas été créé.")
            continue

        chunks = Chunker(str(fichier_markdown))
        insert_documents_into_qdrant(chunks)  # Mise à jour de la variable globale

if __name__ == "__main__":
    load_the_database()
    print("Database loaded successfully")
