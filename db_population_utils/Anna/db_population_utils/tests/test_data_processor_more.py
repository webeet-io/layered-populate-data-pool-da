import pandas as pd
from db_population_utils import DataProcessor, GeoBounds

def test_summary_contains_component_stats():
    df = pd.DataFrame({"A": ["N/A", "ok"], "lat": [52.5, 52.4], "lng": [13.4, 13.5]})
    dp = DataProcessor(verbose=False)

    df1 = dp.standardize_columns(df)
    df2 = dp.clean_webscraping_artifacts(df1)

    bounds = GeoBounds(lat_min=52.3, lat_max=52.7, lng_min=13.0, lng_max=13.8)
    dp.validate_berlin_data(df2, action="mark", berlin_only_plz=True, bounds=bounds)

    df3, _ = dp.prepare_for_ml(df2, strategy="minimal", null_strategy="mark")

    s = dp.get_processing_summary(df3)
    assert "component_stats" in s
    assert set(s["component_stats"].keys()) >= {
        "column_standardizer",
        "webscraping_cleaner",
        "data_validator",
        "ml_preparer",
    }
