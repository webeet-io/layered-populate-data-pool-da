from typing import Dict, List
import pandas as pd
from ..base import SegmentationStrategy

class GreenSpacesRuleBasedSegmenter(SegmentationStrategy):
    """Rule-based segmentation for green spaces"""
    
    def __init__(self, threshold_multiplier: float = 1.5):
        self.threshold_multiplier = threshold_multiplier
        
    def segment(self, features: pd.DataFrame) -> Dict[str, List[str]]:
        """Apply rule-based segmentation"""
        avg_green = features['num_green_spaces'].mean()
        avg_area = features['total_green_area'].mean()
        
        results = {}
        for _, row in features.iterrows():
            tags = []
            if row['num_green_spaces'] > avg_green * self.threshold_multiplier:
                tags.append('green')
            if row['total_green_area'] > avg_area * self.threshold_multiplier:
                tags.append('spacious')
            results[row['neighborhood']] = tags
        return results