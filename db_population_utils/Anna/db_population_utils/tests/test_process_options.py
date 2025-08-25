import pandas as pd
from db_population_utils import DataProcessor, GeoBounds

def test_process_runs_optional_steps_when_requested():
    df = pd.DataFrame({
        "plz": ["10115", "99999"],
        "lat": [52.5, 60.0],
        "lng": [13.4, 13.4],
        "scraped": ["N/A", ""],
        "preis": ["1200", "900"],
        "strasse": ["a", "b"],
        "hausnr": ["1", "2"],
    })
    bounds = GeoBounds(lat_min=52.3, lat_max=52.7, lng_min=13.0, lng_max=13.8)
    dp = DataProcessor(verbose=False)

    out, info = dp.process(
        df,
        clean_webscraping=True,
        custom_null_values=[""],
        cast_spec={"preis": "float32"},
        validate_geo=True,
        geo_action="mark",
        berlin_only_plz=True,
        bounds=bounds,
        dedupe_keys=["plz", "strasse", "hausnr"],
        add_id_cols=["plz", "strasse", "hausnr"],
        id_col="sid",
        stable_id_salt="berlin_v1",
        prepare_for_ml="minimal",
        null_strategy="preserve",
    )

    steps = set(info["steps"].keys())
    # alle angeforderten Schritte sollten erscheinen
    assert {"standardize","webscraping_cleaner","cast_types","geo_validation",
            "dedupe","stable_id","ml_preparer"}.issubset(steps)
    # stabile ID erzeugt
    assert "sid" in out.columns and out["sid"].notna().all()

def test_process_no_optional_flags_only_standardize():
    df = pd.DataFrame({" A ": [1, 2], "B": ["x", "y"]})
    dp = DataProcessor(verbose=False)
    out, info = dp.process(df)  # nur Standardisierung
    assert "standardize" in info["steps"]
    # keine anderen Steps
    assert set(info["steps"].keys()) == {"standardize"}
    # einfache Prüfung auf Spaltenbereinigung (lower/trim etc.)
    assert "a" in out.columns and "b" in out.columns
