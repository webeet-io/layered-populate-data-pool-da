import pandas as pd
from db_population_utils.data_processor.column_standardizer import ColumnStandardizer

def test_standardize_basic_and_duplicates():
    df = pd.DataFrame({ " A ": [1], "A": [2], "B-B": [3], "Ümläut!": [4] })
    cs = ColumnStandardizer(verbose=False)
    df2, report = cs.standardize_columns(df)

    assert list(df2.columns) == ["a", "a_1", "b_b", "uemlaeut"]
    assert report["changes_made"] >= 3
    assert report["duplicates_handled"] >= 1

def test_validate_columns_report():
    cols = [" A ", "N@me", "UPPERCASE", "has space", "dup", "dup"]
    cs = ColumnStandardizer(verbose=False)
    rep = cs.validate_column_names(cols)
    assert not rep["valid"]
    assert rep["duplicate_columns"] == 1
    assert any("spaces" in i.lower() for i in rep["issues"])
