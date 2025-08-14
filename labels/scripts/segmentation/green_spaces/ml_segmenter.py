import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from ..base import SegmentationStrategy

class GreenSpacesMLSegmenter(SegmentationStrategy):
    """ML-based segmentation for green spaces"""
    
    def __init__(self, n_clusters: int = 3):
        
        self.n_clusters = n_clusters
        self.model = KMeans(n_clusters=n_clusters, random_state=42)
        self.scaler = StandardScaler()
        
    def segment(self, features: pd.DataFrame):
        # Select and scale numeric features
        numeric_features = features[[
            'green_space_per_capita',
            'maintenance_score',
            'avg_park_size',
            'num_green_spaces'
        ]]
        
        scaled_features = self.scaler.fit_transform(numeric_features)
        
        # Fit model and predict clusters
        clusters = self.model.fit_predict(scaled_features)
        
        # Create dynamic cluster tags based on feature medians
        cluster_tags = self._generate_cluster_tags(features, clusters)
        return cluster_tags
        # return {
        #     row['neighborhood']: cluster_tags[cluster]
        #     for row, cluster in zip(features.to_dict('records'), clusters)
        # }
    
    def _generate_cluster_tags(self, features, clusters):
        """Generate tags for each neighborhood based on its actual features"""
        # Calculate global medians for comparison
        global_medians = features.drop(columns=['neighborhood']).median()
        
        neighborhood_tags = {}
        
        for idx, row in features.iterrows():
            neighborhood = row['neighborhood']
            tags = []
            
            # Maintenance tags
            if row['maintenance_score'] > global_medians['maintenance_score']:
                tags.append('*well_maintained')
            elif row['maintenance_score'] < global_medians['maintenance_score'] * 0.7:
                tags.append('*needs_attention')
            
            # Size tags
            if row['avg_park_size'] > global_medians['avg_park_size']:
                tags.append('*large_park')
            
            # Spaciousness tags
            if row['green_space_per_capita'] > global_medians['green_space_per_capita']:
                tags.append('*spacious')
            elif row['green_space_per_capita'] < global_medians['green_space_per_capita'] * 0.5:
                tags.append('*crowded')
            
            # Quantity tags
            if row['num_green_spaces'] > global_medians['num_green_spaces']:
                tags.append('*many_parks')
            
            # Add cluster-based tags (prefix with cluster_)
            #tags.append(f'#cluster_{clusters[idx]}')
            
            neighborhood_tags[neighborhood] = tags if tags else ['*average']
        
        return neighborhood_tags