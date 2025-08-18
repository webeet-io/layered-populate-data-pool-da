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
            name = name.split ('#')[0]
            
            if name in features:
                result = segmenter.segment(features[name])
                self.result_aggregator.add_result(name, result)
                
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
        
    def heatmap(self, data: pd.DataFrame, title: str, save_path: str):
        ax2 = sns.heatmap(
                data,
                cmap=["#f0f0f0", "#4c72b0"],                
                linewidths=.5,            
                annot=False,
                fmt=""    
            )
        ax2.set_title(title)
        ax2.set_xlabel("Tags")
        ax2.set_ylabel("Neighborhood")
        #plt.xticks(rotation=45)
        plt.tight_layout()
        if save_path is not None:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

    def network_graph(self, data: pd.DataFrame, title: str, save_path: str):
        plt.figure(figsize=(16, 12))
        G = nx.Graph()                
                # Add nodes with attributes
        for _, row in data.iterrows():
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
        
        if save_path is not None:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
                

    def visualize_results(self, results, image_path):
        """Visualize neighborhood segments with improved plots"""
        try:
            neighborhood_tags_heatmap_path = None
            neighborhood_tag_network_path = None
            
            if image_path is not None:
                if not os.path.exists(image_path):
                    os.mkdir(image_path)
                neighborhood_tags_heatmap_path = os.path.join(image_path, "neighborhood_tags_heatmap.png")
                neighborhood_tag_network_path = os.path.join(image_path, "neighborhood_tag_network.png")
            
            # Set style
            sns.set_theme(style="whitegrid")
            plt.rcParams['font.size'] = 10
            
            # Create a copy and expand the segments
            for table_name in results['table_name'].unique():

                neighborhood_tags_heatmap_path = neighborhood_tags_heatmap_path.replace(".png", f"_{table_name}.png")
                neighborhood_tag_network_path = neighborhood_tag_network_path.replace(".png", f"_{table_name}.png")

                df = results[results['table_name']==table_name].copy()

                df['segments'] = df['segments'].str.split(',')           
                
                # 2. Neighborhood Tag Heatmap
                plt.figure(figsize=(10, 8))
                
                # Create a matrix of tags per neighborhood
                tags_expanded = df.explode('segments')
                heatmap_data = pd.crosstab(
                    tags_expanded['neighborhood'],
                    tags_expanded['segments']
                )
                self.heatmap (heatmap_data, "Neighborhood Segment Tags", neighborhood_tags_heatmap_path)

                try:
                    self.network_graph(tags_expanded, "Neighborhood-Tag Network", neighborhood_tag_network_path)
                except ImportError:
                    print("Network visualization skipped (networkx not available)")

                
        except Exception as e:
            print(f"Visualization error: {str(e)}")
        

    def add(self, id: str, segment_types = None):
        """Configure all components for a segment type in the orchestrator
        
        Args:
            segment_type: The segment type name in snake_case format (e.g. 'green_spaces')
            
        Raises:
            NameError: If required component classes cannot be found
        """
        # Convert snake_case to PascalCase
        pascal_case_id = ''.join(word.title() for word in id.split('_'))
        if segment_types is None:
            segment_types = ['gemini', 'ml', 'rule_based', 'rag']
        try:
            # Get component class objects
            DataLoaderClass = globals()[f"{pascal_case_id}DataLoader"]
            FeatureProcessorClass = globals()[f"{pascal_case_id}FeatureProcessor"]

        except KeyError as e:
            raise NameError(f"Required class '{e.args[0]}' not found") from None


        self.add_data_loader(
            id,
            DataLoaderClass()
        )
        self.add_feature_processor(
            id,
            FeatureProcessorClass()
        )

        for segment_type in segment_types:
            pascal_case = ''.join(word.title() for word in segment_type.split('_'))
            segment_id = f"{id}#{segment_type}"
            segmenter_class_name = f"{pascal_case_id}{pascal_case}Segmenter"
            segmenter_class = globals().get(segmenter_class_name)
            if segmenter_class is None:
                raise NameError(f"Segmenter class '{segmenter_class_name} not found")
            self.add_segmenter(
                segment_id,
                segmenter_class()
            )

       
