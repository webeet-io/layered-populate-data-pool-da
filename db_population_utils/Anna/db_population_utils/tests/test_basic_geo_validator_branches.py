# db_population_utils/tests/test_basic_geo_validator_branches.py
import pandas as pd
from db_population_utils import BasicGeoValidator, GeoBounds

def test_no_geo_columns_is_noop():
    df = pd.DataFrame({"foo": [1, 2, 3]})
    v = BasicGeoValidator(berlin_only_plz=False, action="mark", verbose=False)
    out, rep = v.validate(df)

    # same number of rows
    assert len(out) == len(df)
    # validator may add an all-True flag column
    assert "geo_row_is_valid" in out.columns
    assert out["geo_row_is_valid"].all()
    # all original columns unchanged
    assert out.drop(columns=["geo_row_is_valid"]).equals(df)
    # report is still a dict
    assert isinstance(rep, dict)

def test_drop_mode_reports_counts():
    df = pd.DataFrame({"lat":[52.6, 60.0], "lng":[13.2, 13.2], "plz":["10115","99999"]})
    b = GeoBounds(lat_min=52.3, lat_max=52.7, lng_min=13.0, lng_max=13.8)
    v = BasicGeoValidator(bounds=b, berlin_only_plz=True, action="drop", verbose=False)
    out, rep = v.validate(df)
    assert len(out) == 1
    assert any(k in rep for k in ("counts","summary"))
