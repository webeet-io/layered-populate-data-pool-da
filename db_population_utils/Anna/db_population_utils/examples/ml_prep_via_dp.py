"""
Example — ML preparation via DataProcessor.prepare_for_ml
Run (from repo root):  python -m db_population_utils.examples.ml_prep_via_dp
Alternative (direct run): python db_population_utils/db_population_utils/examples/ml_prep_via_dp.py
"""

# --- Fallback, falls direkt gestartet (nicht als -m Modul) ---
if __name__ == "__main__" and __package__ is None:
    import sys, pathlib
    sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))

import pandas as pd
import numpy as np
from db_population_utils.data_processor import DataProcessor


def _as_list(x):
    """Accept list/dict/None -> list of names."""
    if isinstance(x, list):
        return x
    if isinstance(x, dict):
        return list(x.keys())
    return []


def _print_recommendations(info: dict):
    """
    Print recommendations in a robust way:
    - For strategy='full': use dict at strategy_info['ml_recommendations']
    - Otherwise: use top-level list at info['recommendations']
    """
    si = info.get("strategy_info", {}) or {}
    detailed = si.get("ml_recommendations")
    if isinstance(detailed, dict):
        print("Recs keys:", list(detailed.keys()))
        steps = [s.get("step") for s in detailed.get("preprocessing_steps", []) if isinstance(s, dict)]
        print("Preprocessing steps:", steps)
        return

    # Fallback: simple list (all strategies expose this)
    simple = info.get("recommendations", [])
    print("Recs:", simple)


def _print_feature_analysis(info: dict):
    """
    Print feature analysis in a robust way (some versions return lists, others dicts with metrics).
    Expected location (for strategy='full'): info['strategy_info']['feature_analysis']
    """
    si = info.get("strategy_info", {}) or {}
    feat = si.get("feature_analysis")
    if not isinstance(feat, dict):
        print("Feature analysis: (not available)")
        return

    print("Feature analysis keys:", list(feat.keys()))
    summary = {
        "numeric_features": len(_as_list(feat.get("numeric_features"))),
        "categorical_features": len(_as_list(feat.get("categorical_features"))),
        "low_variance_features": _as_list(feat.get("low_variance_features")),
        "high_cardinality_features": _as_list(feat.get("high_cardinality_features")),
        "features_with_nulls": _as_list(feat.get("features_with_nulls")),
    }
    print("Feature analysis summary:", summary)


def main():
    # --- tiny, readable input ---
    df = pd.DataFrame({
        "num": [1, 2, np.nan, 4, 5],
        "cat": ["a", "a", "b", None, "b"],
        "date": ["2024-01-01", "2024-01-02", None, "2024-01-04", "2024-01-05"],
        "target": [0, 1, 0, 1, 1],
    })
    print("=== INPUT ==="); print(df)

    dp = DataProcessor(verbose=True)

    # -------- Strategy 1: minimal + mark (keine Imputation, nur Flags/Optimierung) --------
    df_min, info_min = dp.prepare_for_ml(
        df, strategy="minimal", null_strategy="mark", target_column="target"
    )
    print("\n=== minimal+mark ===")
    print(df_min)

    actions = (info_min.get("strategy_info", {}) or {}).get("actions", [])
    print("Actions:", actions)

    # sanity: *_was_missing columns must exist for 'mark'
    miss_cols = [c for c in df_min.columns if c.endswith("_was_missing")]
    assert miss_cols, "missing-flag columns should exist with null_strategy='mark'"

    # -------- Strategy 2: full + impute (Imputation + Analyse + Empfehlungen) --------
    df_full, info_full = dp.prepare_for_ml(
        df, strategy="full", null_strategy="impute", target_column="target"
    )
    print("\n=== full+impute ===")
    print(df_full)

    # recommendations (detailed dict if available)
    _print_recommendations(info_full)

    # feature analysis (nested under strategy_info)
    _print_feature_analysis(info_full)

    # simple sanity checks for 'full+impute'
    # - no remaining NaNs in columns we imputed (num/cat/date) expected in most implementations
    for col in ("num", "cat", "date"):
        if col in df_full.columns:
            assert df_full[col].isna().sum() == 0, f"column {col} should be imputed in 'full'"

    # - feature analysis present in strategy_info
    assert "strategy_info" in info_full and "feature_analysis" in info_full["strategy_info"], \
        "feature_analysis should be present under strategy_info for 'full' strategy"

    print("\nOK ✓ ML prep examples ran successfully.")


if __name__ == "__main__":
    main()
