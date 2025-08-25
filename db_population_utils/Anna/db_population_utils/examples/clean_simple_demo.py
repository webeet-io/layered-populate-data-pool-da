"""
Quick Start: DataProcessor.clean_simple

Run as module (recommended, from repo folder with pyproject.toml):
    python -m db_population_utils.examples.clean_simple_demo

If you run the file directly, the fallback header below will add the right path.
"""

# Fallback for direct run (without -m):
if __name__ == "__main__" and __package__ is None:
    import sys, pathlib
    # this file: .../db_population_utils/db_population_utils/examples/clean_simple_demo.py
    sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))

import pandas as pd
from db_population_utils.data_processor import DataProcessor

def main():
    df = pd.DataFrame({
        " Address ": ["  Foo Str. 1  ", "Bar-Str. 2", None],
        "PLZ (Zip)": ["10115", "N/A", "--"],
        "Total Price€": ["1200", "N/A", "800"],
        "Notes": ["  —  ", "ok", "null"],
    })

    print("=== INPUT ===")
    print(df)

    dp = DataProcessor(verbose=True)

    # clean_simple:
    # - standardizes column names
    # - DOES NOT change values (no artifact cleanup, no type casting, no geo checks)
    df_out, info = dp.clean_simple(df)

    print("\n=== OUTPUT ===")
    print(df_out)

    # Show what happened
    std = info["steps"]["standardize"]
    print("\nColumns before -> after:")
    for a, b in zip(std["original_columns"], std["final_columns"]):
        print(f"  {a!r} -> {b!r}")

    # tiny sanity check for readers:
    assert list(df_out.columns) == ["address", "plz_zip", "total_price", "notes"]
    print("\nOK ✓ clean_simple ran successfully.")

if __name__ == "__main__":
    main()
