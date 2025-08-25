import pandas as pd
from db_population_utils import MLDataPreparer

def test_full_strategy_triggers_analysis_and_recommendations():
    df = pd.DataFrame({
        "num": [1.0, 2.0, 3.0],
        "cat": ["x", "x", "y"],
        "lat": [52.5, 52.5, 52.4],
        "lng": [13.4, 13.5, 13.6],
        "target": [0, 1, 0],
    })
    prep = MLDataPreparer(verbose=False)
    out, info = prep.prepare_for_ml(df, strategy="full", null_strategy="preserve", target_column="target")
    si = info["strategy_info"]
    assert "feature_analysis" in si
    assert "ml_recommendations" in si
