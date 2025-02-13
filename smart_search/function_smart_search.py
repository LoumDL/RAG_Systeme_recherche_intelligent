
from marker.converters.pdf import PdfConverter # Import PdfConverter here
from marker.models import create_model_dict
from marker.config.parser import ConfigParser
from IPython.display import Markdown
from chonkie import SemanticChunker
from langchain_community.document_loaders import UnstructuredMarkdownLoader

from function_qdrant_bd import query,qdrant






config = {
    "output_format": "markdown",  # This is causing the issue
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
    markdown = converter(file_path)  # Get the JSON data

    # Access the markdown content from the JSON data
    # (assuming 'content' is the key for markdown content)
    #markdown_content = markdown_data['content']

    return markdown  # Return the markdown content



def markdown_file(markdown,i):
    with open(f"fichier{i}.md", "w", encoding="utf-8") as f:
        f.write(markdown.markdown) # Changed 'makdown' to 'markdown'
    print("Fichier Markdown créé avec succès !")
    print(f"fichier{i}.md")




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





"""
file_path = "../isfad_courses/youssaou_aw.pdf"

markdown = extraction_markdown(file_path)

print(markdown.markdown)

# on cree le fichier markdown 
i=0
markdown_file(markdown,i)

"""
"""
# on effectue les chunks 

chunks = Chunker("./fichier0.md")

client, encoder = qdrant(chunks)


question = " mon parcours académique?"

resultats = query(client,encoder,question)
print(resultats[0])

"""














