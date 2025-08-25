"""
Example — Cast types, de-duplication and stable ID via DataProcessor helpers
Run: python -m db_population_utils.examples.dp_04_cast_dedupe_and_stable_id_via_dp
"""

if __name__ == "__main__" and __package__ is None:
    import sys, pathlib
    sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))

import pandas as pd
from db_population_utils.data_processor import DataProcessor

def main():
    df = pd.DataFrame({
        "address": ["foo 1", "bar 2", "bar 2", "baz 3"],
        "plz": ["10115", "14059", "14059", "14199"],
        "price": ["1,200.00", "800", "800", "950"],
    })
    print("=== INPUT ==="); print(df)

    dp = DataProcessor(verbose=False)

    # 1) Cast types (price -> float32), vorher Komma/Punkt normalisieren
    df["price"] = df["price"].str.replace(",", "", regex=False)
    df_cast, cast_rep = dp.cast_types(df, spec={"price": "float32"})
    print("\n=== casted ==="); print(df_cast.dtypes)
    assert str(df_cast["price"].dtype).startswith("float")

    # 2) De-duplication
    df_ded, ded_rep = dp.dedupe(df_cast, keys=["address", "plz"], keep="first")
    print("\n=== deduped ==="); print(df_ded)
    assert df_ded.shape[0] == 3 and ded_rep["removed"] == 1

    # 3) Stable ID
    df_id, id_rep = dp.add_stable_id(df_ded, cols=["address", "plz"], id_col="stable_id", salt="example", length=16)
    print("\n=== with stable_id ==="); print(df_id)
    assert df_id["stable_id"].str.len().eq(16).all()
    print("\nOK ✓ cast + dedupe + stable_id as expected.")

if __name__ == "__main__":
    main()
