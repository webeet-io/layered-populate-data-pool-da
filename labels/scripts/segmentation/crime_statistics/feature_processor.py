from ..base import FeatureProcessor
import pandas as pd
from sklearn.cluster import DBSCAN
import numpy as np

class CrimeStatisticsFeatureProcessor(FeatureProcessor):
    """Processes crime statistics features and applies safety labels"""
    
    def process_features(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """Process raw crime data into features
        
        Args:
            raw_data: DataFrame from data_loader with columns:
                - neighborhood_id, neighborhood_name, population
                - total_crimes, violent_crimes, property_crimes
                - avg_severity, crime_rate_per_100k
                - year, month
                
        Returns:
            DataFrame with processed features and safety labels
        """
        features = raw_data.copy()
        
        # Calculate metrics
        features['violent_rate'] = features['violent_crimes'] * 100000 / features['population']
        features['property_rate'] = features['property_crimes'] * 100000 / features['population']
        
        # Calculate trends (3-month moving average)
        features['violent_trend'] = features.groupby('neighborhood_id')['violent_crimes'].transform(
            lambda x: x.rolling(3, min_periods=1).mean().pct_change()
        )
        features['property_trend'] = features.groupby('neighborhood_id')['property_crimes'].transform(
            lambda x: x.rolling(3, min_periods=1).mean().pct_change()
        )
        
        # Calculate averages for relative comparisons
        avg_crime_rate = features['crime_rate_per_100k'].mean()
        avg_violent_rate = features['violent_rate'].mean()
        
        # Apply label categories
        features['#low-crime'] = features['crime_rate_per_100k'] < avg_crime_rate * 0.7
        features['#high-violence'] = features['violent_rate'] > avg_violent_rate * 1.5
        features['#property-hotspot'] = features['property_rate'] > avg_crime_rate * 1.3
        features['#severe-crimes'] = features['avg_severity'] > 4
        features['#rising-crime'] = features['violent_trend'] > 0.1
        
        return features