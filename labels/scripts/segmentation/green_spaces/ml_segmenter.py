from typing import Dict, List
import pandas as pd
from ..base import SegmentationStrategy

class GreenSpacesMLSegmenter(SegmentationStrategy):
    """ML-based segmentation for green spaces"""
    
    def __init__(self, n_clusters: int = 3):
        from sklearn.cluster import KMeans
        self.n_clusters = n_clusters
        self.model = KMeans(n_clusters=n_clusters)
        
    def segment(self, features: pd.DataFrame) -> Dict[str, List[str]]:
        """Apply ML-based segmentation"""
        # Select only numeric features
        numeric_features = features.select_dtypes(include=['number'])
        
        # Fit model and predict clusters
        clusters = self.model.fit_predict(numeric_features)
        
        # Map clusters to tags
        cluster_tags = {
            0: ['low_green'],
            1: ['medium_green'], 
            2: ['high_green']
        }
        
        return {
            row['neighborhood']: cluster_tags[cluster]
            for row, cluster in zip(features.to_dict('records'), clusters)
        }