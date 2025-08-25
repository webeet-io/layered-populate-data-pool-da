import pandas as pd
import numpy as np
from db_population_utils import WebscrapingDataCleaner

def test_nan_and_strings_handling():
    df = pd.DataFrame({"x":[np.nan,"nan"," NaN ","", "  ", "ok"]})
    c = WebscrapingDataCleaner(custom_null_values=["  "], verbose=False)
    df2, rep = c.clean_webscraping_artifacts(df)
    assert df2["x"].isna().astype('int64').sum() >= 4
    assert rep["total_artifacts_cleaned"] >= 3

def test_history_and_stats_accumulate():
    c = WebscrapingDataCleaner(verbose=False)
    df = pd.DataFrame({"a":["N/A","ok"]})
    for _ in range(3):
        c.clean_webscraping_artifacts(df)
    stats = c.get_cleaning_stats()
    assert stats["total_operations"] == 3
    assert "most_common_artifacts" in stats
