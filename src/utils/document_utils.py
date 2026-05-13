from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def parse_markdown(file_path):
    loader = UnstructuredMarkdownLoader(file_path)
    documents = loader.load()
    return documents

def chunk_documents(documents, chunk_size=1000, overlap=100):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap
    )
    chunks = splitter.split_documents(documents)
    return chunks