from abc import ABC, abstractmethod
from typing import Dict, List
import pandas as pd

class DataLoader(ABC):
    """Base class for loading data from different sources"""
    
    @property
    @abstractmethod
    def query(self) -> str:
        """Return the SQL query for this data source"""
        pass
        
    def load_data(self, engine) -> pd.DataFrame:
        """Load and return raw data as DataFrame using provided engine"""
        return pd.read_sql(self.query, engine)

class FeatureProcessor(ABC):
    """Base class for processing raw data into features"""
    
    @abstractmethod
    def process_features(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """Process raw data into features"""
        pass

class SegmentationStrategy(ABC):
    """Interface for segmentation approaches"""
    
    @abstractmethod
    def segment(self, features: pd.DataFrame) -> Dict[str, List[str]]:
        """Segment neighborhoods based on features"""
        pass

class BaseClusterer(ABC):
    """Base class for clustering implementations"""
    
    @abstractmethod
    def process(self, features_df: pd.DataFrame, engine=None) -> pd.DataFrame:
        """Main processing method that returns cluster labels DataFrame"""
        pass

class BaseTagger(ABC):
    """Base class for tagging implementations"""
    
    @abstractmethod
    def calculate_tags(self, engine) -> pd.DataFrame:
        """Calculate and return tags DataFrame"""
        pass

class ResultAggregator:
    """Combines results from multiple segmentation approaches"""
    
    def __init__(self):
        self.results = []
    
    def add_result(self, result: Dict[str, List[str]]):
        """Add segmentation result to aggregator"""
        self.results.append(result)
    
    def aggregate(self) -> pd.DataFrame:
        """Combine all segmentation results into final output"""
        if not self.results:
            return pd.DataFrame(columns=['neighborhood', 'segments'])
            
        # Convert list of dicts to DataFrame
        combined = []
        for result in self.results:
            for neighborhood, segments in result.items():
                combined.append({
                    'neighborhood': neighborhood,
                    'segments': ','.join(segments)
                })
        
        return pd.DataFrame(combined)