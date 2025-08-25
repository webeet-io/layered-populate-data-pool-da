from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple
import pandas as pd

@dataclass
class GeoBounds:
    lat_min: float = 52.3
    lat_max: float = 52.7
    lng_min: float = 13.0
    lng_max: float = 13.8

class BasicGeoValidator:
    """
    Lightweight, source-agnostic geo/ZIP validation.

    - Auto-detect latitude/longitude/ZIP columns from common aliases.
    - Numeric coercion with `errors="coerce"`.
    - Validity checks:
        * latitude/longitude within configured `GeoBounds`
        * optional Berlin-only ZIP range check (10115–14199)
    - Action:
        * "mark": add boolean validity columns and `geo_row_is_valid`
        * "drop": filter rows to only valid ones

    Returns `(df_out, report)` with detailed counts and configuration echo.
    """
    def __init__(
        self,
        bounds: Optional[GeoBounds] = None,
        berlin_only_plz: bool = False,
        action: str = "mark",  # "mark" | "drop"
        verbose: bool = False
    ):
        self.bounds = bounds or GeoBounds()
        self.berlin_only_plz = berlin_only_plz
        self.action = action
        self.verbose = verbose
        self.lat_candidates = {"lat", "latitude", "y", "breite", "breitengrad"}
        self.lng_candidates = {"lng", "lon", "long", "longitude", "x", "laenge", "längengrad"}

    def _find_column(self, cols: pd.Index, candidates: set[str]) -> Optional[str]:
        lower_map = {c.lower(): c for c in cols}
        for cand in candidates:
            if cand in lower_map:
                return lower_map[cand]
        return None

    def _validate_plz_series(self, s: pd.Series, berlin_only: bool) -> pd.Series:
        if s is None:
            return pd.Series(index=[], dtype=bool)
        s_str = s.astype("string").str.strip()
        is_5d = s_str.str.fullmatch(r"\d{5}", na=False)
        if not berlin_only:
            return is_5d
        s_num = pd.to_numeric(s_str.where(is_5d), errors="coerce")
        in_range = (s_num >= 10115) & (s_num <= 14199)
        return is_5d & in_range

    def validate(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        if df is None or df.empty:
            return df, {"checked": False, "reason": "empty", "counts": {}, "columns": {}}

        df_out = df.copy()

        lat_col = self._find_column(df_out.columns, self.lat_candidates)
        lng_col = self._find_column(df_out.columns, self.lng_candidates)
        plz_col = self._find_column(df_out.columns, {"plz", "postal_code", "postcode", "zip"})

        if lat_col is not None:
            df_out[lat_col] = pd.to_numeric(df_out[lat_col], errors="coerce")
        if lng_col is not None:
            df_out[lng_col] = pd.to_numeric(df_out[lng_col], errors="coerce")

        lat_valid = pd.Series(True, index=df_out.index)
        lng_valid = pd.Series(True, index=df_out.index)
        if lat_col is not None:
            lat = df_out[lat_col]
            lat_valid = lat.between(self.bounds.lat_min, self.bounds.lat_max, inclusive="both").fillna(False)
        if lng_col is not None:
            lng = df_out[lng_col]
            lng_valid = lng.between(self.bounds.lng_min, self.bounds.lng_max, inclusive="both").fillna(False)

        plz_valid = pd.Series(True, index=df_out.index)
        if plz_col is not None:
            plz_valid = self._validate_plz_series(df_out[plz_col], self.berlin_only_plz).fillna(False)

        combined_valid = pd.Series(True, index=df_out.index)
        if (lat_col is not None) or (lng_col is not None):
            combined_valid &= (lat_valid & lng_valid)
        if plz_col is not None:
            combined_valid &= plz_valid

        if self.action == "drop":
            before = len(df_out)
            df_out = df_out[combined_valid].copy()
            dropped = before - len(df_out)
        else:
            if lat_col is not None:
                df_out[f"{lat_col}_is_valid"] = lat_valid
            if lng_col is not None:
                df_out[f"{lng_col}_is_valid"] = lng_valid
            if plz_col is not None:
                df_out[f"{plz_col}_is_valid"] = plz_valid
            df_out["geo_row_is_valid"] = combined_valid
            dropped = 0

        report = {
            "checked": True,
            "columns": {"lat": lat_col, "lng": lng_col, "plz": plz_col},
            "counts": {
                "rows": int(len(df)),
                "invalid_lat": int((~lat_valid).sum()) if lat_col is not None else 0,
                "invalid_lng": int((~lng_valid).sum()) if lng_col is not None else 0,
                "invalid_plz": int((~plz_valid).sum()) if plz_col is not None else 0,
                "invalid_combined": int((~combined_valid).sum()),
                "dropped": int(dropped),
            },
            "bounds": self.bounds.__dict__,
            "berlin_only_plz": self.berlin_only_plz,
            "action": self.action,
        }
        if self.verbose:
            print(f"[BasicGeoValidator] {report['counts']}")
        return df_out, report
