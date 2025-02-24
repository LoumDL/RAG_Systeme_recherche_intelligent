from word_processing_function import extraction_markdown, markdown_file, Chunker
from vector_database import insert_documents_into_qdrant, query_qdrant
from pathlib import Path

 

def load_the_database():

    # Récupérer les fichiers PDF
    chemin_dossier = Path("/home/dame/djibyloum/RAG_Hakili/RAG_Systeme_recherche_intelligent/isfad_courses") 
    fichiers_pdf = [str(f) for f in chemin_dossier.glob("*.pdf")] 

    for i, file_path in enumerate(fichiers_pdf):
        
        markdown = extraction_markdown(file_path)

        #print(markdown.markdown)

        markdown_file(markdown, i)

        chunks = Chunker(f"./fichier{i}.md")

        client = insert_documents_into_qdrant(chunks)
    
    return client




"""


client = load_the_database()

# Effectuer une requête après l'insertion des documents
question = "quel est le role de l'expert fiscale ?"
resultats = query_qdrant(question, client)
print(resultats)
"""

