"""
Example — Geo validation (mark vs drop) via DataProcessor.process
Run: python -m db_population_utils.examples.dp_03_geo_validation_via_process
"""

if __name__ == "__main__" and __package__ is None:
    import sys, pathlib
    sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))

import pandas as pd
from db_population_utils.data_processor import DataProcessor, GeoBounds

def build_input():
    return pd.DataFrame({
        "Lat": [52.52, 99.00, None, 52.40],
        "Longitude": [13.40, 8.0, 13.30, None],
        "plz": ["10115", "ABCDE", "14059", "99999"],
        "name": ["A", "B", "C", "D"],
    })

def run(action: str):
    dp = DataProcessor(verbose=True)
    df = build_input()
    out, info = dp.process(
        df,
        validate_geo=True,
        geo_action=action,          # "mark" oder "drop"
        berlin_only_plz=True,
        bounds=GeoBounds(),
        prepare_for_ml="preserve",
    )
    print(f"\n=== ACTION={action} ==="); print(out)
    print("Report:", info["steps"]["geo_validation"])
    return out, info

def main():
    mark_df, mark_info = run("mark")
    drop_df, drop_info = run("drop")

    # Mini-Checks
    assert "geo_row_is_valid" in mark_df.columns
    assert drop_df.shape[0] == 1
    print("\nOK ✓ mark produced flags; drop kept only the fully valid row.")

if __name__ == "__main__":
    main()
