import pandas as pd
from db_population_utils import WebscrapingDataCleaner

def test_detect_patterns_and_accumulate_stats():
    df = pd.DataFrame({
        "html": ["<div>1</div>", "ok", "<span>t</span>"],
        "short": ["x", "yy", "toolong"],
        "garbage": ["N/A", "—", "ok"],
        "emptyish": ["", "  ", "ok"],
    })
    c = WebscrapingDataCleaner(custom_null_values=["  "], verbose=False)

    det = c.detect_potential_artifacts(df)
    # at least one column flagged for patterns (html/short/garbage/empty)
    assert det.get("columns_with_patterns", 0) >= 1

    # run cleaner twice to accumulate stats/history
    for _ in range(2):
        df2, rep = c.clean_webscraping_artifacts(df)

    stats = c.get_cleaning_stats()
    assert stats.get("total_operations", 0) >= 2
    # verify that our custom null was considered
    assert "  " in rep.get("null_values_used", [])
    # empty strings should have been treated as nulls
    assert df2["emptyish"].isna().sum() >= 1
