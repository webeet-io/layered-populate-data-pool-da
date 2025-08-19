from typing import Dict, List
import pandas as pd
from ..base import SegmentationStrategy

class GreenSpacesRuleBasedSegmenter(SegmentationStrategy):
    """Rule-based segmentation for green spaces"""
    
    def __init__(self, threshold_multiplier: float = 1.0):
        self.threshold_multiplier = threshold_multiplier
        
    def segment(self, features: pd.DataFrame):
        
        median_maintenance = features['maintenance_score'].median()
        median_size = features['avg_park_size'].median()  
        median_per_capita = features['green_space_per_capita'].median()
        median_parks = features['num_green_spaces'].median()

        # 4. Create labels
        features['#well-maintained'] = features['maintenance_score'] > median_maintenance
        features['#needs-attention'] = features['maintenance_score'] < (median_maintenance * 0.7)
        features['#large-park'] = features['avg_park_size'] > median_size
        features['#spacious'] = features['green_space_per_capita'] > median_per_capita
        features['#crowded'] = features['green_space_per_capita'] < median_per_capita * 0.5
        features['#many-parks'] = features['num_green_spaces'] > median_parks

        result_dict = {}
        for _, row in features.iterrows():
            tags = []
            if row['#well-maintained']:
                tags.append('#well-maintained')
            if row['#needs-attention']:
                tags.append('#needs-attention')
            if row['#large-park']:
                tags.append('#large-park')
            if row['#spacious']:
                tags.append('#spacious')
            if row['#many-parks']:
                tags.append('#many-parks')
            if row['#crowded']:
                tags.append('#crowded')
            result_dict[row['neighborhood']] = tags
        
        return result_dict