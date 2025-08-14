import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict
import pandas as pd
from sqlalchemy import create_engine
import networkx as nx
import os

from segmentation import *
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
        
    def run_pipeline(self, store_results_in_db = False) -> pd.DataFrame:
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
            if name.endswith("_rule_based"):
                name = name.replace("_rule_based", "")  # Get base segment type
            elif name.endswith("_ml"):
                name = name.replace("_ml", "")  # Get base segment type
            
            if name in features:
                result = segmenter.segment(features[name])
                self.result_aggregator.add_result(result)
                
        # 4. Aggregate results
        final_results = self.result_aggregator.aggregate()
        
        # 5. Store results
        if store_results_in_db:
            self._store_results(final_results)

        
        return final_results
        
    def _store_results(self, results: pd.DataFrame):
        """Store results in database using shared engine"""
        results.to_sql('neighborhood_segments', self.engine,
                      if_exists='replace', index=False)
        
    def visualize_results(self, results, image_path="viz"):
        """Visualize neighborhood segments with improved plots"""
        try:
            if not os.path.exists(image_path):
                os.mkdir(image_path)
            neighborhood_tags_heatmap_path = os.path.join(image_path, "neighborhood_tags_heatmap.png")
            neighborhood_tag_network_path = os.path.join(image_path, "neighborhood_tag_network.png")
            # Set style
            sns.set_theme(style="whitegrid")
            plt.rcParams['font.size'] = 10
            
            # Create a copy and expand the segments
            df = results.copy()
            df['segments'] = df['segments'].str.split(',')           
            
            # 2. Neighborhood Tag Heatmap
            plt.figure(figsize=(10, 8))
            
            # Create a matrix of tags per neighborhood
            tags_expanded = df.explode('segments')
            heatmap_data = pd.crosstab(
                tags_expanded['neighborhood'],
                tags_expanded['segments']
            )


            ax2 = sns.heatmap(
                heatmap_data,
                cmap=["#f0f0f0", "#4c72b0"],                
                linewidths=.5,            
                annot=False,
                fmt=""    
            )
            ax2.set_title("Neighborhood Segment Tags")
            ax2.set_xlabel("Tags")
            ax2.set_ylabel("Neighborhood")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(neighborhood_tags_heatmap_path, dpi=300, bbox_inches='tight')
            plt.close()

            try:
                import networkx as nx
                
                plt.figure(figsize=(16, 12))
                G = nx.Graph()
                
                # Add nodes with attributes
                for _, row in tags_expanded.iterrows():
                    G.add_node(row['neighborhood'], 
                            type='neighborhood',
                            size=800)
                    G.add_node(row['segments'], 
                            type='tag',
                            size=600)
                    G.add_edge(row['neighborhood'], row['segments'])
                
                # Improved layout algorithm
                pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
                
                # Separate node types for styling
                neighborhoods = [n for n in G.nodes if G.nodes[n]['type'] == 'neighborhood']
                tags = [n for n in G.nodes if G.nodes[n]['type'] == 'tag']
                
                # Draw with better parameters
                nx.draw_networkx_nodes(
                    G, pos,
                    nodelist=neighborhoods,
                    node_color='skyblue',
                    node_size=800,
                    alpha=0.9,
                    edgecolors='black',
                    linewidths=1
                )
                
                nx.draw_networkx_nodes(
                    G, pos,
                    nodelist=tags,
                    node_color='salmon',
                    node_size=600,
                    alpha=0.9,
                    edgecolors='black',
                    linewidths=1
                )
                
                nx.draw_networkx_edges(
                    G, pos,
                    width=1,
                    alpha=0.3,
                    edge_color='gray'
                )
                
                # Improved label drawing
                nx.draw_networkx_labels(
                    G, pos,
                    font_size=10,
                    font_family='sans-serif',
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=1)
                )
                
                # Add legend
                plt.scatter([], [], c='skyblue', label='Neighborhoods')
                plt.scatter([], [], c='salmon', label='Tags')
                plt.legend(scatterpoints=1, frameon=True, labelspacing=1)
                
                plt.title("Neighborhood-Tag Relationship Network", pad=20)
                plt.axis('off')
                plt.tight_layout()
                plt.savefig(neighborhood_tag_network_path, dpi=300, bbox_inches='tight')
                plt.close()
                
            except ImportError:
                print("Network visualization skipped (networkx not available)")
                
        except Exception as e:
            print(f"Visualization error: {str(e)}")
    def add(self, segment_type: str):
        """Configure all components for a segment type in the orchestrator
        
        Args:
            segment_type: The segment type name in snake_case format (e.g. 'green_spaces')
            
        Raises:
            NameError: If required component classes cannot be found
        """
        # Convert snake_case to PascalCase
        pascal_case = ''.join(word.title() for word in segment_type.split('_'))
        
        try:
            # Get component class objects
            DataLoaderClass = globals()[f"{pascal_case}DataLoader"]
            FeatureProcessorClass = globals()[f"{pascal_case}FeatureProcessor"]
            RuleBasedSegmenterClass = globals()[f"{pascal_case}RuleBasedSegmenter"]
            MLSegmenterClass = globals()[f"{pascal_case}MLSegmenter"]
        except KeyError as e:
            raise NameError(f"Required class '{e.args[0]}' not found") from None


        self.add_data_loader(
            segment_type,
            DataLoaderClass()
        )
        self.add_feature_processor(
            segment_type,
            FeatureProcessorClass()
        )
        self.add_segmenter(
            segment_type + "_rule_based",
            RuleBasedSegmenterClass(threshold_multiplier=1.5)
        )
        self.add_segmenter(
            segment_type + "_ml",
            MLSegmenterClass(n_clusters=3)
        )

    
