from __future__ import annotations
from typing import Dict, Any, Tuple, Optional, Iterable, Callable
import hashlib  
import re   

import pandas as pd

from .column_standardizer import ColumnStandardizer
from .webscraping_cleaner import WebscrapingDataCleaner
from .ml_data_preparer import MLDataPreparer
from .basic_geo_validator import BasicGeoValidator, GeoBounds


class DataProcessor:
    """
    High-level orchestration for data preparation pipelines.

    Pipeline stages:
      1) Column standardization (always)
      2) Optional: web-scraping cleanup
      3) Optional: dtype casting (explicit spec)
      4) Optional: basic geo/ZIP validation ("mark" or "drop")
      5) Optional: de-duplication by key columns
      6) Optional: stable row id from selected columns (SHA-256, shortened)
      7) Optional: ML preparation (strategy: "minimal" | "preserve" | "full"; null handling)

    Each executed step contributes a report dictionary under `info["steps"][<step-name>]`.
    Guaranteed step names (if executed): "standardize", "webscraping_cleaner",
    "cast_types", "geo_validation", "dedupe", "stable_id", "ml_preparer".
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.column_standardizer = ColumnStandardizer(verbose=verbose)
        self.webscraping_cleaner = WebscrapingDataCleaner(verbose=verbose)
        self.ml_preparer = MLDataPreparer(verbose=verbose)

    # -------------------------
    # Pipeline
    # -------------------------
    def process(
        self,
        df: pd.DataFrame,
        *,
        # bestehende Schalter
        clean_webscraping: bool = False,
        prepare_for_ml: Optional[str] = None,     # "minimal" | "preserve" | "full" | None
        null_strategy: str = "preserve",          # "preserve" | "mark" | "impute"
        validate_geo: bool = False,
        geo_action: str = "mark",                 # "mark" | "drop"
        berlin_only_plz: bool = False,
        bounds: Optional[GeoBounds] = None,
        # neu: Parameter für optionale Schritte
        custom_null_values: Optional[list[str]] = None,  # nur für Webscraping-Cleanup
        cast_spec: Optional[dict[str, str]] = None,      # z.B. {"preis":"float32"}
        dedupe_keys: Optional[list[str]] = None,         # z.B. ["plz","lat","lng"]
        add_id_cols: Optional[list[str]] = None,         # z.B. ["strasse","hausnr","plz"]
        id_col: str = "stable_id",
        stable_id_salt: Optional[str] = None,
        stable_id_length: int = 16,                      # HEX-Länge (gerade Zahl)
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        info: Dict[str, Any] = {"steps": {}}
        """Run the configurable end-to-end pipeline. Returns (processed_df, info_report)."""

        # 1) standardize (always)
        df1, rep_std = self.column_standardizer.standardize_columns(df)
        info["steps"]["standardize"] = rep_std
        
        orig = {
            "dedupe_keys": dedupe_keys,
            "add_id_cols": add_id_cols,
            "cast_spec": cast_spec,
        }
        dedupe_keys = self._std_key_list(dedupe_keys)
        add_id_cols = self._std_key_list(add_id_cols)
        cast_spec   = self._std_cast_spec(cast_spec)

        info["steps"]["param_standardization"] = {
            "dedupe_keys_in": orig["dedupe_keys"],
            "dedupe_keys_out": dedupe_keys,
            "add_id_cols_in": orig["add_id_cols"],
            "add_id_cols_out": add_id_cols,
            "cast_spec_in": orig["cast_spec"],
            "cast_spec_out": cast_spec,
        }

        # 2) optional: Web-Scraping-Cleanup
        df2 = df1
        if clean_webscraping:
            cleaner = (
                self.webscraping_cleaner
                if custom_null_values is None
                else WebscrapingDataCleaner(custom_null_values=custom_null_values, verbose=self.verbose)
            )
            df2, rep_clean = cleaner.clean_webscraping_artifacts(df1)
            info["steps"]["webscraping_cleaner"] = rep_clean

        # 3) optional: Typ-Casts (leichtgewichtig, explizites Spec)
        df3 = df2
        if cast_spec:
            df3, rep_cast = self.cast_types(df2, cast_spec)
            info["steps"]["cast_types"] = rep_cast

        # 4) optional: Geo/PLZ-Validation
        df4 = df3
        if validate_geo:
            validator = BasicGeoValidator(
                bounds=bounds,
                berlin_only_plz=berlin_only_plz,
                action=geo_action,
                verbose=self.verbose,
            )
            df4, rep_geo = validator.validate(df3)
            info["steps"]["geo_validation"] = rep_geo

        # 5) optional: Dedupe
        df5 = df4
        if dedupe_keys:
            df5, rep_ded = self.dedupe(df4, keys=dedupe_keys)
            info["steps"]["dedupe"] = rep_ded

        # 6) optional: stabile Zeilen-ID
        df6 = df5
        if add_id_cols:
            df6, rep_id = self.add_stable_id(
                df5,
                cols=add_id_cols,
                id_col=id_col,
                salt=stable_id_salt,
                length=stable_id_length,
            )
            info["steps"]["stable_id"] = rep_id

        # 7) optional: ML-Prep
        df7 = df6
        if prepare_for_ml is not None:
            df7, rep_ml = self.ml_preparer.prepare_for_ml(
                df6, strategy=prepare_for_ml, null_strategy=null_strategy
            )
            info["steps"]["ml_preparer"] = rep_ml

        return df7, info

    # -------------------------
    # Other Pipelines
    # -------------------------
    def clean_simple(self, df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
        """Shortcut: standardize + minimal ML prep (nulls preserved/marked), no geo/web cleanup."""
        return self.process(
            df,
            clean_webscraping=False,
            prepare_for_ml="minimal",
            null_strategy="preserve",
            validate_geo=False,
        )

    def clean_with_webscraping(self, df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
        """Shortcut: standardize + web-scraping cleanup + minimal ML prep."""
        return self.process(
            df,
            clean_webscraping=True,
            prepare_for_ml="minimal",
            null_strategy="preserve",
            validate_geo=False,
        )

    def clean_with_geo_validation(
        self,
        df: pd.DataFrame,
        *,
        geo_action: str = "mark",          # "mark" or "drop"
        berlin_only_plz: bool = True,
        bounds: Optional[GeoBounds] = None,
    ) -> tuple[pd.DataFrame, dict]:
        """Shortcut: standardize + geo/ZIP validation + minimal ML prep."""
        return self.process(
            df,
            clean_webscraping=False,
            prepare_for_ml="minimal",
            null_strategy="preserve",
            validate_geo=True,
            geo_action=geo_action,
            berlin_only_plz=berlin_only_plz,
            bounds=bounds,
        )
    def standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return a copy with standardized column names."""
        df2, _ = self.column_standardizer.standardize_columns(df)
        return df2
    
    def clean_webscraping_artifacts(
        self,
        df: pd.DataFrame,
        *,
        custom_null_values: Optional[list[str]] = None,) -> pd.DataFrame:
        """Clean web-scraping artifacts using the cleaner (constructor-level null values)."""
        cleaner = (
            self.webscraping_cleaner
            if custom_null_values is None
            else WebscrapingDataCleaner(
                custom_null_values=custom_null_values,
                verbose=self.verbose,
            )
        )
        df2, _ = cleaner.clean_webscraping_artifacts(df)
        return df2
    
    def validate_berlin_data(
        self,
        df: pd.DataFrame,
        *,
        action: str = "mark",                 # "mark" | "drop"
        berlin_only_plz: bool = True,
        bounds: Optional[GeoBounds] = None,) -> Dict[str, Any]:
        """Run basic geo/ZIP validation and return ONLY the report (not the modified df)."""
        validator = BasicGeoValidator(
            bounds=bounds,
            berlin_only_plz=berlin_only_plz,
            action=action,
            verbose=self.verbose,
        )
        _, report = validator.validate(df)
        return report
    
    def prepare_for_ml(
        self,
        df: pd.DataFrame,
        *,
        strategy: str = "minimal",
        null_strategy: str = "preserve",
        target_column: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Delegate to MLDataPreparer and return (df_out, info)."""
        return self.ml_preparer.prepare_for_ml(
            df,
            strategy=strategy,
            null_strategy=null_strategy,
            target_column=target_column,
        )
    def get_processing_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Liefert eine stabile, einfache Zusammenfassung.
        Wichtig: enthält immer den Schlüssel 'component_stats',
        damit Tests robust bleiben.
        """
        # Versuche optionale Stats der Komponenten abzufragen; sonst leere Dicts.
        std_stats = {}
        try:
            # falls du später Stats sammelst
            std_stats = getattr(self.column_standardizer, "get_stats", lambda: {})()
        except Exception:
            pass

        ws_stats = {}
        try:
            # WebscrapingDataCleaner hat meist get_cleaning_stats()
            ws_stats = getattr(self.webscraping_cleaner, "get_cleaning_stats", lambda: {})()
        except Exception:
            pass

        ml_stats = {}
        try:
            ml_stats = getattr(self.ml_preparer, "get_stats", lambda: {})()
        except Exception:
            pass

        return {
            "component_stats": {
                "column_standardizer": std_stats,
                "webscraping_cleaner": ws_stats,
                "data_validator": {},   # aktuell keine persistierten Stats
                "ml_preparer": ml_stats,
            },
            "meta": {"version": "0.1.0"},
        }
        
    def dedupe(self, df: pd.DataFrame, keys: Iterable[str], keep: str = "first"):
        """Drop duplicates by key columns; returns (df_out, {"removed":..., "keys":..., "keep":...})."""
        keys = list(keys)
        out = df.drop_duplicates(subset=keys, keep=keep)
        info = {"removed": int(len(df) - len(out)), "keys": keys, "keep": keep}
        return out, info

    def cast_types(self, df: pd.DataFrame, spec: dict[str, str]):
        """Best-effort dtype casting per column, e.g. {'price': 'float32'}. Returns (df_out, report)."""
        out = df.copy()
        changed: dict[str, str] = {}
        for col, dtype in spec.items():
            if col in out.columns:
                try:
                    out[col] = out[col].astype(dtype)
                    changed[col] = dtype
                except Exception:
                    pass  # bewusst still: best-effort
        return out, {"cast": changed}

    @staticmethod
    def _default_normalize(x) -> str:
        if pd.isna(x):
            return ""
        s = str(x).strip().lower()
        return re.sub(r"\s+", " ", s)

    def add_stable_id(
        self,
        df: pd.DataFrame,
        cols: Iterable[str],
        id_col: str = "stable_id",
        *,
        normalize: Callable[[object], str] | None = None,
        salt: str | None = None,
        length: int = 16,  # HEX-Länge (gerade Zahl)
    ):
        """
        Add a deterministic row id based on selected columns.
        Uses SHA-256 over a normalized join of values; `length` is the number of hex characters (must be positive, even).
        Returns (df_out, report).
        """
        if length % 2 != 0 or length <= 0:
            raise ValueError("length muss eine positive, gerade Zahl sein (HEX-Zeichen).")
        cols = list(cols)
        for c in cols:
            if c not in df.columns:
                raise KeyError(f"Spalte '{c}' fehlt für add_stable_id")

        norm = normalize or self._default_normalize
        sep = "|"
        parts = [df[c].map(norm) for c in cols]
        key_series = parts[0]
        for p in parts[1:]:
            key_series = key_series + sep + p
        if salt:
            key_series = salt + "::" + key_series

        def hfun(s: str) -> str:
            return hashlib.sha256(s.encode("utf-8")).hexdigest()[:length]

        out = df.copy()
        out[id_col] = key_series.map(hfun)
        info = {
            "id_col": id_col,
            "from_cols": cols,
            "salt_used": bool(salt),
            "hash": "sha256",
            "hex_len": length,
            "separator": sep,
            "null_handling": "NaN->''; trim; lowercase; collapse whitespace",
        }
        return out, info
    
    def _std_keys(self, keys):
        if not keys:
            return keys
        def clean(s: str) -> str:
            s = s.strip().lower()
            s = re.sub(r"\s+", "_", s)
            s = re.sub(r"[^a-z0-9_]", "", s)
            return s
        return [clean(k) for k in keys]
    
    @staticmethod
    def _std_colname(name: str) -> str:
        s = str(name).strip().lower()
        s = re.sub(r"\s+", "_", s)
        s = re.sub(r"[^a-z0-9_]", "", s)
        return s

    @classmethod
    def _std_key_list(cls, keys):
        if not keys:
            return keys
        return [cls._std_colname(k) for k in keys]

    @classmethod
    def _std_cast_spec(cls, spec):
        if not spec:
            return spec
        return {cls._std_colname(k): v for k, v in spec.items()}






