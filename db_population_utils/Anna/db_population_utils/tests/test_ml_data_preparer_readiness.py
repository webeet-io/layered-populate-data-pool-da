import pandas as pd
from db_population_utils import MLDataPreparer

def test_assess_ml_readiness_paths():
    df = pd.DataFrame({
        "x":[1,None,3,None],
        "y":["a","b","c","d"],
        "z":[1.0,2.0,3.0,4.0],
    })
    prep = MLDataPreparer(verbose=False)
    a = prep.assess_ml_readiness(df, target_column=None)
    assert a["readiness_level"] in {"not_ready","needs_work","mostly_ready","ready"}
    assert "detailed_scores" in a
