import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from ..base import GeminiSegmentationStrategy

class GreenSpacesGeminiSegmenter(GeminiSegmentationStrategy):
    def __init__(self, n_clusters=3):
        super().__init__(n_clusters)

    def segment(self, features: pd.DataFrame):
        # Step 1: Cluster neighborhoods
        numeric_features = features[['green_space_per_capita', 'maintenance_score', 
                                   'avg_park_size', 'num_green_spaces']]
        scaled_features = self.scaler.fit_transform(numeric_features)
        clusters = self.model.fit_predict(scaled_features)
        features['cluster'] = clusters

        # Step 2: Compute cluster summaries
        cluster_summaries = features.groupby('cluster').median(numeric_only=True)

        # Step 3: Generate Gemini-powered tags
        cluster_tags = {}
        for cluster_id in range(self.n_clusters):
            summary = cluster_summaries.loc[cluster_id].to_dict()
            prompt = self._create_prompt(summary)
            llm_tags = self._get_gemini_tags(prompt)
            cluster_tags[cluster_id] = llm_tags

        # Step 4: Assign tags to neighborhoods
        return {
            row['neighborhood']: cluster_tags[row['cluster']]
            for _, row in features.iterrows()
        }

    def _create_prompt(self, cluster_summary: dict) -> str:
        """Generate a prompt for Gemini with cluster statistics"""
        return f"""
        Analyze these green space statistics:

        Cluster Profile:
        - Green space per capita: {cluster_summary['green_space_per_capita']:.2f}
        - Maintenance score: {cluster_summary['maintenance_score']:.2f}
        - Average park size: {cluster_summary['avg_park_size']:.2f}
        - Number of green spaces: {cluster_summary['num_green_spaces']:.2f}

        Suggest 3-6 hyphenated tags (e.g., 'well-maintained') that:
        1. Reflect the quantitative characteristics
        2. Are descriptive and meaningful
        3. Are consistent with similar neighborhoods

        Return ONLY comma-separated tags, nothing else:
        """
