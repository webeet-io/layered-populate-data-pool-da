"""
Example 02 — Basic geo/ZIP validation (mark vs drop)
Run: python -m examples.02_basic_geo_validation
"""

import pandas as pd
from db_population_utils import BasicGeoValidator, GeoBounds

def main():
    # Mischmasch aus gültigen/ungültigen Werten
    df = pd.DataFrame({
        "Lat": [52.52, 99.0, None, 52.40],
        "Longitude": [13.40, 8.0, 13.30, None],
        "plz": ["10115", "ABCDE", "14059", "99999"],
        "name": ["A", "B", "C", "D"],
    })

    print("=== Input ===")
    print(df)

    # Variante 1: markieren (Flags + geo_row_is_valid)
    validator_mark = BasicGeoValidator(
        bounds=GeoBounds(), berlin_only_plz=True, action="mark", verbose=True
    )
    df_mark, rep_mark = validator_mark.validate(df)
    print("\n=== Mark action ===")
    print(df_mark)
    print("Report:", rep_mark)

    # Variante 2: ungültige Zeilen dropen
    validator_drop = BasicGeoValidator(
        bounds=GeoBounds(), berlin_only_plz=True, action="drop", verbose=True
    )
    df_drop, rep_drop = validator_drop.validate(df)
    print("\n=== Drop action ===")
    print(df_drop)
    print("Report:", rep_drop)

if __name__ == "__main__":
    main()
