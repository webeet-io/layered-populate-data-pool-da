from typing import Dict, List
import pandas as pd
from ..base import FeatureProcessor

class GreenSpacesFeatureProcessor(FeatureProcessor):
    """Processes green space features"""
    
    def process_features(self, raw_data):
        features = raw_data.copy()

        # 1. Calculate core metrics
        features['green_space_per_capita'] = (
            features['total_green_area'] / 
            features['population'].replace(0, 1)
        )
        # 2. Maintenance scoring (lower years = better)
        features['maintenance_score'] = (
            10 - features['avg_years_since_renovation'].clip(0, 20) / 2
        )

        features['maintenance_score'] =  features['maintenance_score'].fillna(0)
        features['green_space_per_capita'] = features['green_space_per_capita'].fillna(1)
        return features
        