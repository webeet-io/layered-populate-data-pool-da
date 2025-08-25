"""
Example — Column standardization + Webscraping cleanup (via DataProcessor helpers)
Run (from repo root): python -m db_population_utils.examples.dp_01_standardize_and_clean_via_dp
"""

# Fallback, falls direkt gestartet (nicht als -m Modul):
if __name__ == "__main__" and __package__ is None:
    import sys, pathlib
    sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))

import pandas as pd
from db_population_utils import DataProcessor

def main():
    df = pd.DataFrame({
        " Address ": ["  Foo Str. 1  ", "Bar-Str. 2", None],
        "PLZ (Zip)": ["10115", "N/A", "--"],
        "Total Price€": ["1.200", "N/A", "800"],
        "Notes": ["  —  ", "ok", "null"],
    })
    print("=== INPUT ==="); print(df)

    dp = DataProcessor(verbose=True)

    # 1) Spalten standardisieren
    df1 = dp.standardize_columns(df)
    print("\n=== standardized ==="); print(df1)
    assert list(df1.columns) == ["address", "plz_zip", "total_price", "notes"]

    # 2) Webscraping-Artefakte bereinigen (mit eigenem Token)
    df2 = dp.clean_webscraping_artifacts(df1, custom_null_values=["—", "1.200"])
    print("\n=== cleaned ==="); print(df2)

    # Mini-Checks
    assert df2["plz_zip"].isna().sum() == 2
    assert df2["total_price"].isna().sum() == 2
    assert df2["notes"].isna().sum() == 1
    print("\nOK ✓ basic cleaning expectations met.")

if __name__ == "__main__":
    main()
