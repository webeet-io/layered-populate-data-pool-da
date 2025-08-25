import numpy as np
import pandas as pd
from db_population_utils import MLDataPreparer

def test_dtype_optimization_reports_memory():
    df = pd.DataFrame({
        "i64": np.array([1,2,3], dtype="int64"),
        "f64": np.array([1.0,2.0,3.0], dtype="float64"),
        "cat": ["a","a","b"],
    })
    prep = MLDataPreparer(verbose=False)
    out, info = prep.prepare_for_ml(df, strategy="minimal", null_strategy="preserve")
    mem = info["strategy_info"]["optimization_info"]["memory_saved"]
    assert {"original_memory_bytes","final_memory_bytes","memory_saved_bytes","memory_saved_percentage"} <= mem.keys()
