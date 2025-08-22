import pandas as pd
from db_population_utils.data_processor.berlin_data_validator import BerlinDataValidator

def test_helpers_detect_columns():
    df = pd.DataFrame({
        "created_date": ["2024-01-01", "2024-02-01"],
        "lat": [52.5, 52.4],
        "lng": [13.4, 13.5],
        "user_mail": ["a@b.de", "x@y.com"]
    })
    v = BerlinDataValidator(verbose=False)
    assert "created_date" in v._detect_date_columns(df)
    assert set(v._detect_coordinate_columns(df)) >= {"lat","lng"}
    assert "user_mail" in v._detect_email_columns(df)

def test_coordinate_validation_and_business_rules():
    df = pd.DataFrame({
        "lat": ["52.5", "55.1"],     # second is out of range
        "lng": ["13.0", "15.0"],     # second out of range
        "plz": ["10115", "99999"],   # second invalid for Berlin
        "price": [1000, -1],
        "area_m2": [50, 0]
    })
    v = BerlinDataValidator(verbose=False)
    rep = v.validate_berlin_data(df)
    assert rep["total_issues"] >= 3
    s = v.get_validation_stats()
    assert s["total_runs"] == 1
