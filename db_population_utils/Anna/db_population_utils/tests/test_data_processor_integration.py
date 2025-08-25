import pandas as pd
from db_population_utils import DataProcessor, GeoBounds

def test_end_to_end_pipeline_minimal(tmp_path):
    df = pd.DataFrame({
        "  PLZ ": ["10115", "99999", " 12345 "],
        " lat ": [52.52, 55.0, 52.3],
        "lng": [13.4, 10.0, 13.1],
        "E-Mail": ["a@b.de", "not-an-email", "x@y.com"],
        " Preis ": [1200, -5, 900],
        " area_m2 ": [50, 0, 70],
        " scraped ": ["N/A", "ok", ""]
    })

    dp = DataProcessor(verbose=False)

    # 1) standardize
    df1 = dp.standardize_columns(df)
    assert {"plz", "lat", "lng"}.issubset(df1.columns)

    # 2) clean webscraping artifacts (treat empty string as null)
    df2 = dp.clean_webscraping_artifacts(df1, custom_null_values=[""])
    assert df2["scraped"].isna().astype("int64").sum() >= 1

    # 3) basic geo validation (using BasicGeoValidator under the hood)
    bounds = GeoBounds(lat_min=52.3, lat_max=52.7, lng_min=13.0, lng_max=13.8)
    val_report = dp.validate_berlin_data(df2, action="mark", berlin_only_plz=True, bounds=bounds)
    assert isinstance(val_report, dict)

    # 4) minimal ML prep with null markers
    df3, ml_info = dp.prepare_for_ml(df2, strategy="minimal", null_strategy="mark")
    assert any(c.endswith("_was_missing") for c in df3.columns)
    assert "strategy_info" in ml_info

    # 5) processing summary (no ProcessingMetadata anymore)
    summary = dp.get_processing_summary(df3)
    assert "component_stats" in summary
