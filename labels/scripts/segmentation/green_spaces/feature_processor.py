from typing import Dict, List
import pandas as pd
from ..base import FeatureProcessor

class GreenSpacesFeatureProcessor(FeatureProcessor):
    """Processes green space features"""
    
    def process_features(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """Calculate derived green space features"""
        features = raw_data.copy()
        
        # Only calculate per capita if population > 0
        features['green_space_per_capita'] = 0
        mask = features['population'] > 0
        features.loc[mask, 'green_space_per_capita'] = (
            features.loc[mask, 'total_green_area'] /
            features.loc[mask, 'population']
        )
        
        # Add additional safety checks
        # Convert to numeric types before calculations
        features = features.astype({
            'population': 'float64',
            'total_green_area': 'float64',
            'num_green_spaces': 'int32'
        })
        
        # Only calculate per capita if population > 0
        features['green_space_per_capita'] = 0.0
        mask = (features['population'] > 0) & (features['total_green_area'] > 0)
        features.loc[mask, 'green_space_per_capita'] = (
            features.loc[mask, 'total_green_area'].astype('float64') /
            features.loc[mask, 'population'].astype('float64')
        )
        
        return features