from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.config.parser import ConfigParser
from IPython.display import Markdown
from chonkie import SemanticChunker
from langchain_community.document_loaders import UnstructuredMarkdownLoader

# Configuration du système
config = {
    "output_format": "markdown",  # Format de sortie en Markdown
    "ADDITIONAL_KEY": "VALUE"      # Clé supplémentaire pour la configuration
}
config_parser = ConfigParser(config)

def extraction_markdown(file_path: str):
    """
    Convertit un fichier PDF en Markdown à l'aide d'un convertisseur spécifique.
    
    Args:
        file_path (str): Chemin du fichier PDF à convertir.
    
    Returns:
        str: Contenu du fichier converti en Markdown.
    """
    converter = PdfConverter(
        config=config_parser.generate_config_dict(),
        artifact_dict=create_model_dict(),
        processor_list=config_parser.get_processors(),
        renderer=config_parser.get_renderer()
    )
    markdown = converter(file_path)   
    return markdown  

def markdown_file(markdown, fichier_markdown):
    """
    Enregistre le contenu Markdown dans un fichier.
    
    Args:
        markdown (str): Contenu Markdown à enregistrer.
        fichier_markdown (str): Chemin du fichier où sauvegarder le Markdown.
    """
    with open(fichier_markdown, "w", encoding="utf-8") as f:
        f.write(markdown.markdown)

def Chunker(markdown_path):
    """
    Divise un fichier Markdown en segments sémantiques (chunks) pour un traitement NLP.
    
    Args:
        markdown_path (str): Chemin du fichier Markdown à segmenter.
    
    Returns:
        list: Liste des segments sémantiques extraits.
    """
    loader = UnstructuredMarkdownLoader(markdown_path)
    data = loader.load()
    
    chunker = SemanticChunker(
        embedding_model="minishlab/potion-base-8M",
        threshold=0.5,
        chunk_size=512,
        min_sentences=1
    )

    batch_chunks = chunker.chunk_batch([doc.page_content for doc in data])
    chunk_table = []

    for doc_chunks in batch_chunks:
        for i, chunk in enumerate(doc_chunks, start=1):
            chunk_table.append([i, chunk.text])  # Ajout dans un tableau (liste de listes)

    return chunk_table
