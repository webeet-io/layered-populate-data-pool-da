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
        features['#well_maintained'] = features['maintenance_score'] > median_maintenance
        features['#needs_attention'] = features['maintenance_score'] < (median_maintenance * 0.7)
        features['#large_park'] = features['avg_park_size'] > median_size
        features['#spacious'] = features['green_space_per_capita'] > median_per_capita
        features['#crowded'] = features['green_space_per_capita'] < median_per_capita * 0.5
        features['#many_parks'] = features['num_green_spaces'] > median_parks

        result_dict = {}
        for _, row in features.iterrows():
            tags = []
            if row['#well_maintained']:
                tags.append('#well_maintained')
            if row['#needs_attention']:
                tags.append('#needs_attention')
            if row['#large_park']:
                tags.append('#large_park')
            if row['#spacious']:
                tags.append('#spacious')
            if row['#many_parks']:
                tags.append('#many_parks')
            if row['#crowded']:
                tags.append('#crowded')
            result_dict[row['neighborhood']] = tags
        
        return result_dict