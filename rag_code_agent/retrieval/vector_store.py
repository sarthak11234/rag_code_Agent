import numpy as np
import json
import os
import pickle
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

class VectorStore:
    def __init__(self, persistence_path: str = "./data/vector_store.pkl"):
        self.persistence_path = persistence_path
        self.documents = []
        self.metadatas = []
        self.embeddings = None
        
        # Initialize model - forcing CPU to avoid torch/cuda issues if possible, though ST usually handles it.
        # Use a small model.
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Warning: Failed to load SentenceTransformer: {e}")
            self.model = None

        self.load()

    def add_chunks(self, chunks: List[Any]):
        """Expected chunks from CodeChunker."""
        new_docs = []
        new_metas = []
        
        for chunk in chunks:
            new_docs.append(chunk.content)
            new_metas.append({
                "file_path": chunk.file_path,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "type": chunk.type,
                "name": chunk.name
            })
            
        if not new_docs:
            return

        # Encode
        if self.model:
            print("Generating embeddings...")
            new_embeds = self.model.encode(new_docs)
            
            if self.embeddings is None:
                self.embeddings = new_embeds
            else:
                self.embeddings = np.vstack([self.embeddings, new_embeds])
                
        self.documents.extend(new_docs)
        self.metadatas.extend(new_metas)
        self.save()

    def query(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        if self.model is None or self.embeddings is None or len(self.documents) == 0:
            return []

        query_embed = self.model.encode([query_text])[0]
        
        # Cosine similarity
        # (A . B) / (|A| * |B|)
        scores = np.dot(self.embeddings, query_embed) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embed)
        )
        
        # Get top N indices
        top_k_indices = np.argsort(scores)[::-1][:n_results]
        
        results = []
        for idx in top_k_indices:
            results.append({
                "content": self.documents[idx],
                "metadata": self.metadatas[idx],
                "score": float(scores[idx])
            })
            
        return results

    def save(self):
        os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
        with open(self.persistence_path, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'metadatas': self.metadatas,
                'embeddings': self.embeddings
            }, f)

    def load(self):
        if os.path.exists(self.persistence_path):
            with open(self.persistence_path, 'rb') as f:
                data = pickle.load(f)
                self.documents = data['documents']
                self.metadatas = data['metadatas']
                self.embeddings = data['embeddings']
