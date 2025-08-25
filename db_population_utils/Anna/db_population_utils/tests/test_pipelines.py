import pandas as pd
from db_population_utils import DataProcessor, GeoBounds

def test_clean_simple_pipeline_smoke():
    df = pd.DataFrame({"A":[1, None, 3], "B":["x", "y", None]})
    dp = DataProcessor(verbose=False)
    out, info = dp.clean_simple(df)
    assert isinstance(out, pd.DataFrame)
    assert out.shape[0] == 3
    # Make sure both steps ran
    assert "standardize" in info["steps"]
    assert "ml_preparer" in info["steps"]

def test_clean_with_webscraping_pipeline_smoke():
    df = pd.DataFrame({"scraped":["N/A", "", "ok"], "num":[1,2,3]})
    dp = DataProcessor(verbose=False)
    out, info = dp.clean_with_webscraping(df)
    assert out["scraped"].isna().sum() >= 2
    assert "webscraping_cleaner" in info["steps"]

def test_clean_with_geo_validation_pipeline_smoke():
    df = pd.DataFrame({"plz":["10115", "99999"], "lat":[52.5, 60.0], "lng":[13.4, 13.4]})
    bounds = GeoBounds(lat_min=52.3, lat_max=52.7, lng_min=13.0, lng_max=13.8)
    dp = DataProcessor(verbose=False)
    out, info = dp.clean_with_geo_validation(df, geo_action="mark", berlin_only_plz=True, bounds=bounds)
    assert any(c.endswith("_is_valid") for c in out.columns)
    assert "geo_validation" in info["steps"]
