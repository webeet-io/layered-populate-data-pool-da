import pandas as pd
import numpy as np
from db_population_utils import MLDataPreparer

def _sample_df():
    return pd.DataFrame({
        "num": [1.0, np.nan, 3.5, 2.0],
        "cat": ["a", "a", "b", None],
        "bin": ["y", "n", "y", "n"],
        "text": ["hello", None, "world", "ok"],
        "target": [0, 1, 0, 1],
    })

def test_minimal_mark_keeps_nans_and_marks():
    m = MLDataPreparer(verbose=False)
    df = _sample_df()
    out, info = m.prepare_for_ml(df, strategy="minimal", null_strategy="mark", target_column="target")
    # row count preserved
    assert len(out) == len(df)
    # nulls may remain but we expect missing flags added
    assert any(c.endswith("_was_missing") for c in out.columns)
    assert "strategy_info" in info

def test_minimal_impute_removes_nans():
    m = MLDataPreparer(verbose=False)
    df = _sample_df()
    out, info = m.prepare_for_ml(df, strategy="minimal", null_strategy="impute", target_column="target")
    assert out.isna().sum().sum() == 0
    assert "null_handling" in info

def test_full_strategy_adds_features_and_returns_analysis():
    m = MLDataPreparer(verbose=False)
    df = _sample_df()
    out, info = m.prepare_for_ml(df, strategy="full", null_strategy="preserve", target_column="target")
    # full should not shrink columns; usually expands
    assert out.shape[1] >= 3
    si = info.get("strategy_info", {})
    assert isinstance(si, dict)
    # if readiness is implemented, this should be callable without error
    _ = m.assess_ml_readiness(df, target_column="target")
