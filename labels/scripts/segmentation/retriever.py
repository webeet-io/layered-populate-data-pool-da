import os
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

class VectorRetriever:
    """RAG implementation for neighborhood context retrieval"""
    
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.knowledge_base = []
        self.embeddings = np.array([])
        self.nn = NearestNeighbors(n_neighbors=3)
        
    def add_documents(self, documents: List[Dict]):
        """Add documents to knowledge base with metadata"""
        self.knowledge_base.extend(documents)
        texts = [doc['text'] for doc in documents]
        new_embeddings = self.model.encode(texts)
        
        if len(self.embeddings) == 0:
            self.embeddings = new_embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, new_embeddings])
            
        self.nn.fit(self.embeddings)
    
    def retrieve(self, query: str, k=3) -> List[Dict]:
        """Retrieve relevant documents for a query"""
        query_embedding = self.model.encode([query])
        distances, indices = self.nn.kneighbors(query_embedding)
        
        return [self.knowledge_base[i] for i in indices[0]]