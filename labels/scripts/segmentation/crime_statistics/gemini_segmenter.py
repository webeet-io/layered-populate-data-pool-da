import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from ..base import GeminiSegmentationStrategy

class CrimeStatisticsGeminiSegmenter(GeminiSegmentationStrategy):
    def __init__(self, n_clusters=3):
        super().__init__(n_clusters)

    def segment(self, features: pd.DataFrame):
        # Step 1: Cluster neighborhoods
        imputer = SimpleImputer(strategy="mean")
        numeric_features = imputer.fit_transform(features[['crime_rate_per_100k',
                                                   'violent_rate',
                                                   'property_rate',
                                                   'avg_severity']])
        
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
            row['neighborhood_name']: cluster_tags[row['cluster']]
            for _, row in features.iterrows()
        }

    def _create_prompt(self, cluster_summary: dict) -> str:
        """Generate a prompt for Gemini with crime statistics"""
        return f"""
        Analyze these crime statistics:

        Cluster Profile:
        - Crime rate per 100k: {cluster_summary['crime_rate_per_100k']:.2f}
        - Violent crime rate: {cluster_summary['violent_rate']:.2f}
        - Property crime rate: {cluster_summary['property_rate']:.2f}
        - Average severity: {cluster_summary['avg_severity']:.2f}

        Suggest 3-6 hyphenated tags (e.g., 'high-crime') that:
        1. Reflect the quantitative characteristics
        2. Are descriptive and meaningful
        3. Are consistent with similar neighborhoods

        Return ONLY comma-separated tags, nothing else:
        """