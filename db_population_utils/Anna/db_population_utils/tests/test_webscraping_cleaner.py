import pandas as pd
from db_population_utils import WebscrapingDataCleaner

def test_clean_artifacts_basic():
    df = pd.DataFrame({"x": ["N/A", "ok", "", "  ", "nan"], "y": [1,2,3,4,5]})
    cleaner = WebscrapingDataCleaner(custom_null_values=["  "], verbose=False)
    df2, rep = cleaner.clean_webscraping_artifacts(df)

    assert df2["x"].isna().astype('int64').sum() >= 3
    assert rep["total_artifacts_cleaned"] >= 3
    assert "x" in rep["affected_columns"]

def test_detect_potential_artifacts():
    df = pd.DataFrame({"html": ["<div>1</div>", "x", "y"], "short": ["a", "b", "ccc"]})
    cleaner = WebscrapingDataCleaner(verbose=False)
    det = cleaner.detect_potential_artifacts(df)
    assert det["columns_with_patterns"] >= 1
    assert "recommendation" in det
