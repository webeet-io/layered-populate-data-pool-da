import pandas as pd
from ..base import SegmentationStrategy
from ..retriever import VectorRetriever
import json
import os

class GreenSpacesRagSegmenter(SegmentationStrategy):
    def __init__(self):
        # Initialize RAG components
        self.retriever = VectorRetriever()
        rag_file_path = os.path.join(os.path.dirname(__file__), 'rag_docs.json')
        if os.path.isfile(rag_file_path):
            with open(rag_file_path, 'r') as f:
                rag_docs = json.load(f)
                self.retriever.add_documents(rag_docs)

    def segment(self, features: pd.DataFrame):
        # For each neighborhood, find matching tags from rag_docs
        results = {}
        for _, row in features.iterrows():
            query = f"""
            Green space characteristics:
            - Per capita: {row['green_space_per_capita']:.2f}
            - Maintenance: {row['maintenance_score']:.2f}
            - Park size: {row['avg_park_size']:.2f}
            - Quantity: {row['num_green_spaces']:.2f}
            """
            context_docs = self.retriever.retrieve(query)
            # Get all unique tags from matching documents
            tags = set()
            for doc in context_docs:
                tags.update(doc.get('tags', []))
            results[row['neighborhood']] = list(tags)
        
        return results