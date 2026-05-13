from sentence_transformers import SentenceTransformer
from pinecone import Pinecone as PineconeClient
from src.config import PINECONE_API_KEY, PINECONE_INDEX_NAME
from rank_bm25 import BM25Okapi
import json
import os

# Global cache for expensive objects
_embeddings_cache = None
_pinecone_index_cache = None
_bm25_cache = None
_corpus_docs_cache = None

class RetrieveTool:
    def __init__(self):
        # Lazy initialization - defer until first use
        self.pc = None
        self.index = None
        self.embeddings = None
        self.bm25 = None
        self.corpus_docs = []
        self.doc_map = {}
    
    def _ensure_initialized(self):
        """Lazy initialization of expensive resources."""
        global _embeddings_cache, _pinecone_index_cache, _bm25_cache, _corpus_docs_cache
        
        if self.embeddings is None:
            print("Initializing embeddings model...")
            if _embeddings_cache is None:
                _embeddings_cache = SentenceTransformer('all-MiniLM-L6-v2')
            self.embeddings = _embeddings_cache
        
        if self.index is None:
            print("Connecting to Pinecone...")
            if _pinecone_index_cache is None:
                self.pc = PineconeClient(api_key=PINECONE_API_KEY)
                _pinecone_index_cache = self.pc.Index(PINECONE_INDEX_NAME)
            self.index = _pinecone_index_cache
        
        if not self.corpus_docs and _corpus_docs_cache is None:
            print("Building BM25 index...")
            self._build_bm25_index()
            _corpus_docs_cache = self.corpus_docs
        elif _corpus_docs_cache is not None and not self.corpus_docs:
            self.corpus_docs = _corpus_docs_cache
    
    def _build_bm25_index(self):
        """Build in-memory BM25 index for keyword search."""
        corpus_path = "policy_corpus"
        if not os.path.exists(corpus_path):
            return
        
        from pathlib import Path
        from PyPDF2 import PdfReader
        from docx import Document
        
        for file_path in Path(corpus_path).rglob("*"):
            suffix = file_path.suffix.lower()
            if suffix not in [".md", ".pdf", ".docx"] or not file_path.is_file():
                continue
            
            try:
                if suffix == ".md":
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read()
                elif suffix == ".pdf":
                    reader = PdfReader(file_path)
                    text = "\n\n".join([page.extract_text() for page in reader.pages])
                elif suffix == ".docx":
                    doc = Document(file_path)
                    text = "\n\n".join([p.text for p in doc.paragraphs])
                else:
                    continue
                
                doc_id = file_path.stem
                self.doc_map[doc_id] = text
                self.corpus_docs.append({"doc_id": doc_id, "text": text})
            except Exception:
                continue
        
        # Build BM25 corpus
        if self.corpus_docs:
            tokenized_corpus = [doc["text"].split() for doc in self.corpus_docs]
            self.bm25 = BM25Okapi(tokenized_corpus)
        else:
            self.bm25 = None

    def _run(self, query: str, top_k: int = 5) -> str:
        """Hybrid retrieval: combine dense embeddings + BM25 keyword search."""
        self._ensure_initialized()
        
        results_dict = {}
        
        # Dense retrieval (semantic similarity)
        query_embedding = self.embeddings.encode(query).tolist()
        dense_results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        for match in dense_results['matches']:
            doc_id = match['metadata'].get('doc_id', '')
            if doc_id not in results_dict:
                results_dict[doc_id] = {'dense_score': 0, 'bm25_score': 0, 'metadata': match['metadata']}
            results_dict[doc_id]['dense_score'] = match['score']
        
        # Sparse retrieval (BM25 keyword search)
        if self.bm25 and self.corpus_docs:
            query_tokens = query.split()
            bm25_scores = self.bm25.get_scores(query_tokens)
            for idx, score in enumerate(bm25_scores):
                if score > 0 and idx < len(self.corpus_docs):
                    doc_id = self.corpus_docs[idx]['doc_id']
                    if doc_id not in results_dict:
                        results_dict[doc_id] = {'dense_score': 0, 'bm25_score': 0, 'metadata': {'doc_id': doc_id, 'text': self.corpus_docs[idx]['text']}}
                    results_dict[doc_id]['bm25_score'] = float(score) / (max(bm25_scores) + 1e-6)  # normalize
        
        # Combine scores: 70% dense, 30% BM25
        combined_results = []
        for doc_id, scores in results_dict.items():
            combined_score = 0.7 * scores.get('dense_score', 0) + 0.3 * scores.get('bm25_score', 0)
            combined_results.append({
                'doc_id': doc_id,
                'content': scores['metadata'].get('text', '')[:500],  # Truncate for size
                'score': combined_score,
                'dense_score': scores.get('dense_score', 0),
                'bm25_score': scores.get('bm25_score', 0)
            })
        
        # Sort by combined score and return top-k
        combined_results.sort(key=lambda x: x['score'], reverse=True)
        return json.dumps(combined_results[:top_k])

class GetDocumentMetadataTool:
    def __init__(self):
        self.metadata = None

    def _ensure_metadata_loaded(self):
        """Lazy load metadata from corpus."""
        if self.metadata is None:
            metadata_path = "policy_corpus/metadata.json"
            if os.path.exists(metadata_path):
                with open(metadata_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
            else:
                self.metadata = {}

    def _run(self, doc_id: str) -> str:
        self._ensure_metadata_loaded()
        return json.dumps(self.metadata.get(doc_id, {}))

class CheckContradictionsTool:
    def _run(self, doc_ids: str) -> str:
        try:
            doc_list = json.loads(doc_ids)
        except:
            doc_list = doc_ids.split(',')
        
        if len(doc_list) > 1:
            return "Potential contradictions detected between documents: " + ", ".join(doc_list)
        return "No contradictions detected"