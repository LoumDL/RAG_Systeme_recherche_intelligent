
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.config.parser import ConfigParser
from IPython.display import Markdown
from chonkie import SemanticChunker
from langchain_community.document_loaders import UnstructuredMarkdownLoader





config = {
    "output_format": "markdown",  
    "ADDITIONAL_KEY": "VALUE"
}
config_parser = ConfigParser(config)




def extraction_markdown(file_path: str):
    converter = PdfConverter(
        config=config_parser.generate_config_dict(),
        artifact_dict=create_model_dict(),
        processor_list=config_parser.get_processors(),
        renderer=config_parser.get_renderer()
    )
    markdown = converter(file_path)   

    return markdown  



def markdown_file(markdown, fichier_markdown):
    with open(fichier_markdown, "w", encoding="utf-8") as f:
        f.write(markdown.markdown)
 


def Chunker(markdown_path):
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

    #return batch_chunks

















