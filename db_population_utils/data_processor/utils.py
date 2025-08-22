# db_population_utils/data_processor/utils.py
import numpy as np
import pandas as pd

def count_true(mask) -> int:
    """
    Robustly count True values in a boolean-like array/Series/Index/DataFrame.
    Works around NumPy/Pandas reduction quirks under coverage.
    """
    if isinstance(mask, (pd.Series, pd.Index)):
        return int(np.count_nonzero(mask.to_numpy()))
    if isinstance(mask, pd.DataFrame):
        # total Trues across all columns/rows
        return int(np.count_nonzero(mask.to_numpy()))
    # generic array-like
    return int(np.count_nonzero(np.asarray(mask)))

def col_null_counts(df: pd.DataFrame) -> dict:
    """
    Null count per column without using .sum() reductions.
    """
    return {col: count_true(df[col].isnull()) for col in df.columns}
