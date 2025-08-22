import pandas as pd
import numpy as np
from db_population_utils.data_processor.ml_data_preparer import MLDataPreparer

def sample_df():
    return pd.DataFrame({
        "num": [1, np.nan, 3, 4],
        "cat": ["a", None, "a", "b"],
        "bin": ["y", "n", "y", "y"],
        "target": [0,1,0,1]
    })

def test_null_mark_and_impute():
    m = MLDataPreparer(verbose=False)
    df = sample_df()
    df_mark, info_m = m.prepare_for_ml(df, strategy="preserve", null_strategy="mark", target_column="target")
    assert any(c.endswith("_was_missing") for c in df_mark.columns)

    df_imp, info_i = m.prepare_for_ml(df, strategy="preserve", null_strategy="impute", target_column="target")
    assert df_imp.isna().astype('int64').sum().sum() == 0
    assert "imputation_summary" in info_i["null_handling"]

def test_minimal_and_full_strategies():
    m = MLDataPreparer(verbose=False)
    df = sample_df()
    df_min, inf_min = m.prepare_for_ml(df, strategy="minimal", null_strategy="preserve", target_column="target")
    assert "optimization_info" in inf_min["strategy_info"]

    df_full, inf_full = m.prepare_for_ml(df, strategy="full", null_strategy="preserve", target_column="target")
    assert "feature_analysis" in inf_full["strategy_info"]
    assert "ml_recommendations" in inf_full["strategy_info"]

def test_assess_ml_readiness_scoring():
    m = MLDataPreparer(verbose=False)
    df = sample_df()
    a = m.assess_ml_readiness(df, target_column="target")
    assert a["readiness_level"] in {"ready","mostly_ready","needs_work","not_ready"}
