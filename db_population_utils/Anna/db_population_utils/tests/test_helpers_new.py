import pandas as pd
from db_population_utils import DataProcessor

def test_dedupe_removes_dupes_and_reports():
    df = pd.DataFrame({"k": [1, 1, 2], "v": [10, 10, 20]})
    dp = DataProcessor(verbose=False)
    out, info = dp.dedupe(df, keys=["k"])
    assert len(out) == 2
    assert info["removed"] == 1
    assert info["keys"] == ["k"]

def test_cast_types_best_effort_and_missing_column_skipped():
    df = pd.DataFrame({"i": ["1", "2"], "f": ["1.5", "2.5"]})
    dp = DataProcessor(verbose=False)
    out, info = dp.cast_types(df, {"i": "int64", "f": "float32", "missing": "int32"})
    assert str(out["i"].dtype).startswith("int")
    assert str(out["f"].dtype).startswith("float")
    # fehlende Spalten tauchen nicht im "cast"-Report auf
    assert set(info["cast"].keys()) == {"i", "f"}

def test_add_stable_id_is_deterministic_and_length_and_salt():
    df = pd.DataFrame({"a": [1, 1], "b": ["X", "x"]})
    dp = DataProcessor(verbose=False)

    out1, info1 = dp.add_stable_id(df, cols=["a", "b"], id_col="sid", length=16)
    out2, info2 = dp.add_stable_id(df, cols=["a", "b"], id_col="sid", length=16)
    # deterministisch bei gleicher Eingabe
    assert out1["sid"].equals(out2["sid"])
    # Länge stimmt
    assert out1["sid"].str.len().unique().tolist() == [16]

    # anderer Salt -> andere IDs
    out3, _ = dp.add_stable_id(df, cols=["a", "b"], id_col="sid", length=16, salt="ns1")
    assert not out1["sid"].equals(out3["sid"])
    # Info-Werte klingen plausibel
    assert info1["hash"] == "sha256" and info1["hex_len"] == 16
