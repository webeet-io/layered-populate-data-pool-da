import pandas as pd


from ..base import DataLoader
from .sql_queries import GREEN_SPACES_QUERY


class GreenSpacesDataLoader(DataLoader):

    @property
    def query(self) -> str:
        return GREEN_SPACES_QUERY
        
    def load_data(self, engine) -> pd.DataFrame:
        df = pd.read_sql(self.query, engine)   
        return df