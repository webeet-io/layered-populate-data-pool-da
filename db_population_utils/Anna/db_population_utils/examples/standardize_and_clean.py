"""
Example 01 — Column standardization + Webscraping cleanup
Run: python -m examples.01_standardize_and_clean
"""

import pandas as pd

from db_population_utils import ColumnStandardizer
from db_population_utils import WebscrapingDataCleaner

def main():
    df = pd.DataFrame({
        " Address ": ["  Foo Str. 1  ", "Bar-Str. 2", None],
        "PLZ (Zip)": ["10115", "N/A", "--"],
        "Total Price€": ["1.200", "N/A", "800"],
        "Notes": ["  —  ", "ok", "null"],
    })

    print("=== Original ===")
    print(df)

    # 1) Spalten standardisieren
    std = ColumnStandardizer(verbose=True)
    df_std, rep_std = std.standardize_columns(df)

    print("\n=== Standardized columns ===")
    print(df_std.head())
    print("Report:", rep_std)

    # 2) Webscraping-Artefakte bereinigen (inkl. eigener Tokens)
    cleaner = WebscrapingDataCleaner(custom_null_values={"—", "1.200"}, verbose=True)
    df_cln, rep_cln = cleaner.clean_webscraping_artifacts(df_std)

    print("\n=== Cleaned dataframe ===")
    print(df_cln.head())

    # Kompatibel zu alten/anderen Report-Schlüsseln:
    artifacts = rep_cln.get("artifacts_found", rep_cln.get("per_column_artifacts", {}))
    print("\nArtifacts per column:")
    if artifacts:
        for col, counts in artifacts.items():
            print(f"  - {col}: {counts}")
    else:
        print("  (none)")

    print("\nSummary:")
    print("  affected_columns:", rep_cln.get("affected_columns"))
    print("  columns_processed:", rep_cln.get("columns_processed"))
    print("  total_artifacts_cleaned:", rep_cln.get("total_artifacts_cleaned"))
    print("  null_values_used:", rep_cln.get("null_values_used"))

    print("\nCleaner state:")
    print("  null-like tokens:", cleaner.get_null_values())
    print("  history length:", len(cleaner.get_cleaning_history()))
    print("  stats:", cleaner.get_cleaning_stats())

if __name__ == "__main__":
    main()
