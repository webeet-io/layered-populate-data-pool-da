from ..base import SegmentationStrategy
import pandas as pd
from typing import Dict, List
class CrimeStatisticsRuleBasedSegmenter(SegmentationStrategy):
    """Rule-based segmentation of neighborhoods by crime statistics"""
    
    def segment(self, features: pd.DataFrame) -> Dict[str, List[str]]:
        """Segment neighborhoods based on crime features
        
        Args:
            features: DataFrame from feature_processor with safety labels
            
        Returns:
            Dictionary mapping neighborhood names to list of tags
        """
        segments = {}
        
        for _, row in features.iterrows():
            tags = []
            neighborhood = row['neighborhood_name']
            
            # Add tags based on feature flags
            if row['#low-crime']:
                tags.append('#safe')
            if row['#high-violence']:
                tags.append('#high-violence') 
            if row['#property-hotspot']:
                tags.append('#property-hotspot')
            if row['#severe-crimes']:
                tags.append('#severe-crimes')
            if row['#rising-crime']:
                tags.append('#rising-crime')
                
            segments[neighborhood] = tags
            
        return segments