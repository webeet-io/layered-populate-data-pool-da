import pandas as pd
from db_population_utils import MLDataPreparer

def test_impute_numeric_and_categorical():
    df = pd.DataFrame({"num":[1.0, None, 3.0], "cat":["a", None, "a"]})
    prep = MLDataPreparer(verbose=False)
    out, info = prep.prepare_for_ml(df, strategy="preserve", null_strategy="impute")
    assert out["num"].isna().sum() == 0
    assert out["cat"].isna().sum() == 0
    assert info["null_handling"]["action"] == "imputed_missing_values"

def test_mark_and_drop_behavior():
    df = pd.DataFrame({"x":[1, None, 3], "y":[None, "a", "b"]})
    prep = MLDataPreparer(verbose=False)
    out_mark, info_mark = prep.prepare_for_ml(df, strategy="preserve", null_strategy="mark")
    assert any(c.endswith("_was_missing") for c in out_mark.columns)

    out_drop, info_drop = prep.prepare_for_ml(df, strategy="preserve", null_strategy="drop")
    assert len(out_drop) < len(df)
    assert "dropped_" in info_drop["null_handling"]["action"]
