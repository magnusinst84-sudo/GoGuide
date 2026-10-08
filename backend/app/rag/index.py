import os
import faiss
import numpy as np
import json
import uuid
import datetime
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
RAG_DIR = BACKEND_ROOT / "data" / "rag"

RAG_ENABLED = os.getenv("RAG_ENABLED", "true").lower() == "true"
RAG_INDEX_PATH = os.getenv("RAG_INDEX_PATH", str(RAG_DIR))
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))
RAG_EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "all-MiniLM-L6-v2")

class Document:
    def __init__(self, doc_id: str, doc_type: str, title: str, text: str, metadata: dict):
        self.doc_id = doc_id
        self.doc_type = doc_type
        self.title = title
        self.text = text
        self.metadata = metadata

class RAGIndex:
    _instance = None
    
    def __init__(self):
        self.index = None
        self.documents = []
        self.manifest = {}
        self.model = None
        self._initialized = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = RAGIndex()
        return cls._instance

    def initialize(self):
        if self._initialized or not RAG_ENABLED:
            return

        index_file = os.path.join(RAG_INDEX_PATH, "index.faiss")
        docs_file = os.path.join(RAG_INDEX_PATH, "documents.jsonl")
        manifest_file = os.path.join(RAG_INDEX_PATH, "manifest.json")

        if not (os.path.exists(index_file) and os.path.exists(docs_file)):
            logger.warning("RAG index files not found. Run the build script.")
            return

        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(RAG_EMBEDDING_MODEL)
        self.index = faiss.read_index(index_file)
        
        with open(docs_file, 'r', encoding='utf-8') as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    doc_data = json.loads(line)
                    self.documents.append(Document(**doc_data))
                except json.JSONDecodeError as e:
                    logger.warning(f"Skipping malformed JSONL line {lineno}: {e}")
                
        if os.path.exists(manifest_file):
            with open(manifest_file, 'r', encoding='utf-8') as f:
                self.manifest = json.load(f)
                
        self._initialized = True

    def retrieve(self, query: str, filters: Dict[str, Any] = None, top_k: int = None) -> List[dict]:
        if not self._initialized:
            self.initialize()
            if not self._initialized:
                return []
                
        if top_k is None:
            top_k = RAG_TOP_K
            
        # Get query embedding
        query_emb = self.model.encode([query])
        
        # FAISS search
        # Search a bit more in case we need to filter
        search_k = top_k * 5 if filters else top_k
        distances, indices = self.index.search(query_emb.astype(np.float32), search_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(self.documents):
                continue
            
            doc = self.documents[idx]
            
            # Apply filters
            if filters:
                skip = False
                for k, v in filters.items():
                    if k == "document_type" and doc.doc_type != v:
                        skip = True
                        break
                    # Add more generic filter matching if needed
                if skip:
                    continue
                    
            results.append({
                "document_id": doc.doc_id,
                "document_type": doc.doc_type,
                "title": doc.title,
                "text": doc.text,
                "score": float(distances[0][i]),
                "metadata": doc.metadata
            })
            
            if len(results) >= top_k:
                break
                
        return results

def retrieve(query: str, filters: Dict[str, Any] = None, top_k: int = None) -> List[dict]:
    index = RAGIndex.get_instance()
    # If not enabled or model not loadable, return empty mock array gracefully
    try:
        return index.retrieve(query, filters, top_k)
    except Exception as e:
        logger.error(f"RAG retrieval failed: {e}")
        return []
