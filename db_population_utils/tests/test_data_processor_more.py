import pandas as pd
from db_population_utils.data_processor.processing_metadata import ProcessingMetadata
from db_population_utils.data_processor.DataProcessor import DataProcessor

def test_summary_contains_component_stats():
    df = pd.DataFrame({"A":["N/A","ok"], "lat":[52.5, 52.4], "lng":[13.4, 13.5]})
    md = ProcessingMetadata(file_path="dummy.csv")
    dp = DataProcessor.with_metadata(md, verbose=False)
    df1 = dp.standardize_columns(df)
    df2 = dp.clean_webscraping_artifacts(df1)
    dp.validate_berlin_data(df2)
    df3, _ = dp.prepare_for_ml(df2, strategy="minimal", null_strategy="mark")

    s = dp.get_processing_summary(df3)
    assert "processing_metadata" in s and "component_stats" in s
    assert set(s["component_stats"].keys()) >= {"column_standardizer","webscraping_cleaner","data_validator","ml_preparer"}
