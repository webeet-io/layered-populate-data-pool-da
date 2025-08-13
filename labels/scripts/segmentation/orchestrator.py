# from segmentation.green_spaces import (
#     GreenSpacesDataLoader,
#     GreenSpacesFeatureProcessor,
#     GreenSpacesRuleBasedSegmenter,
#     GreenSpacesMLSegmenter
# )

from segmentation.green_spaces import *
from typing import Dict
import pandas as pd
from sqlalchemy import create_engine
from .base import DataLoader, FeatureProcessor, SegmentationStrategy, ResultAggregator

class SegmentationOrchestrator:
    """Coordinates the entire segmentation process"""
    
    def __init__(self, db_url: str):  
        self.engine = create_engine(db_url)
        self.data_loaders: Dict[str, DataLoader] = {}
        self.feature_processors: Dict[str, FeatureProcessor] = {}
        self.segmenters: Dict[str, SegmentationStrategy] = {}
        self.result_aggregator = ResultAggregator()
        
    def add_data_loader(self, name: str, loader: DataLoader):
        """Register a data loader"""
        self.data_loaders[name] = loader
        
    def add_feature_processor(self, name: str, processor: FeatureProcessor):
        """Register a feature processor"""
        self.feature_processors[name] = processor
        
    def add_segmenter(self, name: str, segmenter: SegmentationStrategy):
        """Register a segmentation strategy"""
        self.segmenters[name] = segmenter
        
    def run_pipeline(self) -> pd.DataFrame:
        """Run the full segmentation pipeline"""

        # 1. Load all data using shared engine
        raw_data = {}
        for name, loader in self.data_loaders.items():
            raw_data[name] = loader.load_data(self.engine)
            
        # 2. Process features
        features = {}
        for name, processor in self.feature_processors.items():
            if name in raw_data:
                features[name] = processor.process_features(raw_data[name])
                
        # 3. Apply segmentation
        for name, segmenter in self.segmenters.items():
            if name in features:
                result = segmenter.segment(features[name])
                self.result_aggregator.add_result(result)
                
        # 4. Aggregate results
        final_results = self.result_aggregator.aggregate()
        
        # 5. Store results
        self._store_results(final_results)
        
        return final_results
        
    def _store_results(self, results: pd.DataFrame):
        """Store results in database using shared engine"""
        results.to_sql('neighborhood_segments', self.engine,
                      if_exists='replace', index=False)
        
    def visualize_results(self, results: pd.DataFrame):
        """Generate visualizations of segmentation results
        
        Args:
            results: DataFrame containing segmentation results with columns:
                - neighborhood
                - segment_type
                - labels
                - score (optional)
        """
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            # Set style
            sns.set_theme(style="whitegrid")
            
            # Plot distribution of segments
            plt.figure(figsize=(10, 6))
            ax = sns.countplot(
                x="neighborhood",
                hue="labels",
                data=results,
                palette="Set2"
            )
            ax.set_title("Segment Distribution by Type")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig("segment_distribution.png")
            plt.close()
            
            # Plot scores if available
            if "score" in results.columns:
                plt.figure(figsize=(10, 6))
                ax = sns.boxplot(
                    x="segment_label",
                    y="score",
                    hue="segment_type",
                    data=results,
                    palette="Set2"
                )
                ax.set_title("Segment Scores Distribution")
                plt.tight_layout()
                plt.savefig("segment_scores.png")
                plt.close()
                
        except ImportError:
            print("Visualization dependencies not available")
        except Exception as e:
            print(f"Visualization failed: {str(e)}")

    
    def add(self, segment_type: str):
        """Configure all components for a segment type in the orchestrator
        
        Args:
            segment_type: The segment type name in snake_case format (e.g. 'green_spaces')
            
        Raises:
            NameError: If required component classes cannot be found
        """
        # Convert snake_case to PascalCase
        pascal_case = ''.join(word.title() for word in segment_type.split('_'))
        
        # Get component class objects
        DataLoaderClass = globals()[f"{pascal_case}DataLoader"]
        FeatureProcessorClass = globals()[f"{pascal_case}FeatureProcessor"]
        RuleBasedSegmenterClass = globals()[f"{pascal_case}RuleBasedSegmenter"]
        MLSegmenterClass = globals()[f"{pascal_case}MLSegmenter"]
        
        self.add_data_loader(
            segment_type,
            DataLoaderClass()
        )
        self.add_feature_processor(
            segment_type,
            FeatureProcessorClass()
        )
        self.add_segmenter(
            segment_type,
            RuleBasedSegmenterClass(threshold_multiplier=1.5)
        )
        self.add_segmenter(
            segment_type,
            MLSegmenterClass(n_clusters=3)
        )

    
