"""
Example — End-to-end via DataProcessor.process
Run: python -m db_population_utils.examples.dp_02_process_end_to_end
"""

if __name__ == "__main__" and __package__ is None:
    import sys, pathlib
    sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))

import pandas as pd
from db_population_utils import DataProcessor, GeoBounds

def main():
    df = pd.DataFrame({
        " Address ": ["Foo Str. 1", "Bar Str. 2", "Bar Str. 2"],
        "PLZ": ["10115", "ABCDE", "14059"],
        "Lat": [52.5200, 99.0, 52.40],
        "Lng": [13.4050, 8.0, None],
        "Price": ["1200", "N/A", "800"],
        "Category": ["apt", "apt", None],
    })
    print("=== INPUT ==="); print(df)

    dp = DataProcessor(verbose=True)
    df_out, info = dp.process(
        df,
        clean_webscraping=True,
        cast_spec={"Price": "float32"},
        validate_geo=True,
        geo_action="mark",
        berlin_only_plz=True,
        bounds=GeoBounds(),                 # Berlin-Default
        dedupe_keys=["Address", "PLZ"],
        add_id_cols=["Address", "PLZ"],
        id_col="stable_id",
        stable_id_salt="demo",
        prepare_for_ml="minimal",
        null_strategy="mark",
    )

    print("\n=== OUTPUT (head) ==="); print(df_out.head())
    # Defensive: nur ausgeben, wenn Step existiert
    print("\nSteps executed:", list(info.get("steps", {}).keys()))
    geo = info.get("steps", {}).get("geo_validation", {})
    print("Geo counts:", geo.get("counts"))

    # Mini-Checks
    assert "stable_id" in df_out.columns
    assert df_out["stable_id"].notna().all()
    assert df_out.shape[0] >= 1
    print("\nOK ✓ pipeline produced stable ids and non-empty output.")

if __name__ == "__main__":
    main()
