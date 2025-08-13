from ..base import DataLoader
import pandas as pd

class GreenSpacesDataLoader(DataLoader):
    """Loads green space data from database
    
    Attributes:
        engine: SQLAlchemy engine for database connection
    """
    
    def __init__(self):
        """Initialize with default settings"""
        self._columns = [
            'neighborhood',
            'num_green_spaces',
            'total_green_area',
            'population'
        ]
        
    @property
    def query(self) -> str:
        """Return the SQL query for green spaces data"""
        from .sql_queries import GREEN_SPACES_QUERY
        return GREEN_SPACES_QUERY
        
    def load_data(self, engine) -> pd.DataFrame:
        """Load green spaces data from database
        
        Args:
            engine: SQLAlchemy engine instance
            
        Returns:
            DataFrame with green space statistics by neighborhood
        """
        import pandas as pd
        df = pd.read_sql(self.query, engine)
        
        # Validate required columns are present
        missing = set(self._columns) - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
            
        return df[self._columns]