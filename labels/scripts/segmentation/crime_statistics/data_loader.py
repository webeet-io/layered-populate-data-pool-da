from ..base import DataLoader
import pandas as pd
from .sql_queries import CRIME_STATS_QUERY

class CrimeStatisticsDataLoader(DataLoader):
    """Loads crime statistics data from database"""
    
    def __init__(self):
        """Initialize with default settings"""
        self._columns = [
            'neighborhood_id',
            'neighborhood',  # Matches SQL query column alias
            'population',
            'total_crimes',
            'violent_crimes',
            'property_crimes',
            'avg_severity',
            'year',
            'month'
        ]
        
    @property
    def query(self) -> str:
        """Return the SQL query for crime stats"""
        return CRIME_STATS_QUERY
        
    def load_data(self, engine) -> pd.DataFrame:
        """Load crime statistics from database
        
        Args:
            engine: SQLAlchemy engine instance
            
        Returns:
            DataFrame with crime statistics by neighborhood
        """
        df = pd.read_sql(self.query, engine)
        
        # Validate required columns are present
        missing = set(self._columns) - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
            
        # Convert types and rename columns for consistency
        df = df.rename(columns={'neighborhood': 'neighborhood_name'})
        df['neighborhood_id'] = df['neighborhood_id'].astype(str)
        df['year'] = df['year'].astype(int)
        df['month'] = df['month'].astype(int)
        
        # Calculate crime rates
        df['crime_rate_per_100k'] = df['total_crimes'] * 100000 / df['population']
        df['violent_crimes_per_capita'] = df['violent_crimes'] / df['population']
        
        return df