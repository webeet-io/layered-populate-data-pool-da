import pandas as pd
from db_population_utils.data_processor.processing_metadata import ProcessingMetadata
from db_population_utils.data_processor.DataProcessor import DataProcessor

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

    md = ProcessingMetadata(file_path="dummy.csv")
    dp = DataProcessor.with_metadata(md, verbose=False)

    df1 = dp.standardize_columns(df)
    assert "plz" in df1.columns and "lat" in df1.columns

    df2 = dp.clean_webscraping_artifacts(df1, custom_null_values=[""])
    assert df2["scraped"].isna().astype('int64').sum() >= 1

    val = dp.validate_berlin_data(df2)
    assert "validation_details" in val

    df3 = dp.prepare_for_ml(df2, strategy="minimal", null_strategy="mark")[0]
    # Marker-Spalten sollten vorhanden sein wenn Nulls existierten
    assert any(c.endswith("_was_missing") for c in df3.columns)

    # Summary sollte ohne Fehler erzeugbar sein
    summary = dp.get_processing_summary(df3)
    assert "processing_metadata" in summary
