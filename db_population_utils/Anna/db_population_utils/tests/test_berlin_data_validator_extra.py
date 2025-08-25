import pandas as pd
from db_population_utils import BasicGeoValidator, GeoBounds

def test_basic_geo_validation_mark_mode_adds_flags():
    df = pd.DataFrame({
        "lat": [52.5, 55.1],      # second out of bounds
        "lng": [13.4, 15.0],      # second out of bounds
        "plz": ["10115", "99999"] # second not a Berlin PLZ
    })
    bounds = GeoBounds(lat_min=52.3, lat_max=52.7, lng_min=13.0, lng_max=13.8)
    v = BasicGeoValidator(bounds=bounds, berlin_only_plz=True, action="mark", verbose=False)
    
    out_df, report = v.validate(df)
    # mark-mode should NOT drop rows
    assert len(out_df) == len(df)

    # expect *_is_valid markers to exist
    assert any(c.endswith("_is_valid") for c in out_df.columns)

    # report should include some counts/summary of issues
    assert "counts" in report or "summary" in report

def test_basic_geo_validation_drop_mode_drops_invalid_rows():
    df = pd.DataFrame({
        "lat": [52.52, 60.0],     # second invalid
        "lng": [13.4, 13.4],
        "plz": ["10115", "99999"] # second invalid for Berlin
    })
    bounds = GeoBounds(lat_min=52.3, lat_max=52.7, lng_min=13.0, lng_max=13.8)
    v = BasicGeoValidator(bounds=bounds, berlin_only_plz=True, action="drop", verbose=False)
    
    out_df, report = v.validate(df)
    # should drop the invalid second row
    assert len(out_df) == 1
