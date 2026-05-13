import os
import sys
import zipfile
import json
import requests
from pathlib import Path

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from pinecone import Pinecone as PineconeClient
from pinecone import ServerlessSpec
from sentence_transformers import SentenceTransformer
from docx import Document
from PyPDF2 import PdfReader
from src.config import (
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    PINECONE_CLOUD,
    PINECONE_REGION,
    PINECONE_ENV,
    PINECONE_HOST,
    CORPUS_ZIP_URL,
)


def download_and_extract_corpus(url, extract_to="policy_corpus"):
    if os.path.exists(extract_to) and any(Path(extract_to).rglob("*")):
        print("Corpus already exists, skipping download")
        return

    if not url:
        raise ValueError("CORPUS_ZIP_URL is not configured")

    os.makedirs(extract_to, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    zip_path = "corpus.zip"
    with open(zip_path, "wb") as f:
        f.write(response.content)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)

    os.remove(zip_path)


def load_markdown(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def load_pdf(path: str) -> str:
    reader = PdfReader(path)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n\n".join(pages)


def load_docx(path: str) -> str:
    doc = Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)


def load_documents(corpus_path="policy_corpus"):
    documents = []
    metadata_path = os.path.join(corpus_path, "metadata.json")
    metadata = {}
    if os.path.exists(metadata_path):
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

    for file_path in Path(corpus_path).rglob("*"):
        suffix = file_path.suffix.lower()
        if suffix not in [".md", ".pdf", ".docx"] or not file_path.is_file():
            continue

        try:
            if suffix == ".md":
                text = load_markdown(file_path)
            elif suffix == ".pdf":
                text = load_pdf(file_path)
            elif suffix == ".docx":
                text = load_docx(file_path)
            else:
                continue
        except Exception as exc:
            print(f"Error loading {file_path}: {exc}")
            continue

        if not text.strip():
            continue

        doc_id = file_path.stem
        documents.append({
            "doc_id": doc_id,
            "text": text,
            "metadata": metadata.get(doc_id, {})
        })

    return documents


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end].strip())
        start += chunk_size - overlap
    return [chunk for chunk in chunks if chunk]


def ensure_pinecone_index():
    if PINECONE_API_KEY is None:
        raise ValueError("PINECONE_API_KEY is required for ingestion")

    try:
        pc = PineconeClient(api_key=PINECONE_API_KEY)
        existing = pc.list_indexes()
        existing_names = [idx['name'] for idx in existing]

        if PINECONE_INDEX_NAME in existing_names:
            print(f"Using existing Pinecone index: {PINECONE_INDEX_NAME}")
            return pc.Index(PINECONE_INDEX_NAME)

        # Index doesn't exist, try to create it
        if ServerlessSpec and PINECONE_CLOUD and PINECONE_REGION:
            spec = ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION)
            pc.create_index(
                name=PINECONE_INDEX_NAME,
                spec=spec,
                dimension=384,
                metric="cosine",
            )
            print(f"Created new Pinecone index: {PINECONE_INDEX_NAME}")
            return pc.Index(PINECONE_INDEX_NAME)
        else:
            raise ValueError(
                "Pinecone index does not exist and cannot be auto-created without PINECONE_CLOUD and PINECONE_REGION. "
                "Set these environment variables or create the index manually in Pinecone with dimension=384 and metric=cosine."
            )
    except Exception as e:
        print(f"Pinecone error: {e}")
        raise


def create_vector_store(documents):
    if not documents:
        raise ValueError("No documents available to index")

    index = ensure_pinecone_index()
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    vectors = []

    for doc in documents:
        chunks = chunk_text(doc["text"], chunk_size=1000, overlap=100)
        for i, chunk in enumerate(chunks):
            metadata = dict(doc["metadata"])
            metadata.update({"doc_id": doc["doc_id"], "text": chunk})
            vector = embedder.encode(chunk).tolist()
            vector_id = f"{doc['doc_id']}_{i}"
            vectors.append((vector_id, vector, metadata))

    batch_size = 100
    for start in range(0, len(vectors), batch_size):
        index.upsert(vectors=vectors[start : start + batch_size])

    return index


def ingest(corpus_path="policy_corpus"):
    documents = load_documents(corpus_path)
    create_vector_store(documents)


if __name__ == "__main__":
    if CORPUS_ZIP_URL:
        download_and_extract_corpus(CORPUS_ZIP_URL)
    ingest()
    print("Ingestion complete")