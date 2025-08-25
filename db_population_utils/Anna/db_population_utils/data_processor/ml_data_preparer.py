# -*- coding: utf-8 -*-


from __future__ import annotations

import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, UTC

import pandas as pd
import numpy as np
from pandas.api import types as pdt  # NEW

# (importe aus .utils waren ungenutzt, daher entfernt)

logger = logging.getLogger(__name__)


class MLDataPreparer:
    """
    Specialized ML preparation:
      - Null handling strategies: "preserve" | "drop" | "mark" | "impute" | "smart_drop"
      - ML strategy: "preserve" | "minimal" | "full"
          * "minimal": dtype optimization and memory report
          * "full": + feature analysis (numeric/categorical, low-variance, high-cardinality) and recommendations
      - Detailed recommendations and readiness assessment; maintains `preparation_history`.
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.preparation_history: List[Dict[str, Any]] = []

    def prepare_for_ml(
        self,
        df: pd.DataFrame,
        strategy: str = "preserve",
        null_strategy: str = "preserve",
        target_column: Optional[str] = None
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:

        df_copy = df.copy()

        preparation_info: Dict[str, Any] = {
            "original_shape": df_copy.shape,
            "null_counts_before": df_copy.isnull().sum().to_dict(),
            "strategy": strategy,
            "null_strategy": null_strategy,
            "target_column": target_column,
            # NEW: serialisierbar & UTC
            "preparation_timestamp": datetime.now(UTC).isoformat(),
        }

        # 1) Null-Handling
        df_copy, null_handling_info = self._handle_nulls(df_copy, null_strategy, target_column)
        preparation_info["null_handling"] = null_handling_info

        # 2) ML-Strategie
        df_copy, strategy_info = self._apply_ml_strategy(df_copy, strategy, target_column)
        preparation_info["strategy_info"] = strategy_info

        # 3) Abschluss
        preparation_info["final_shape"] = df_copy.shape
        preparation_info["null_counts_after"] = df_copy.isnull().sum().to_dict()
        preparation_info["recommendations"] = self._generate_ml_recommendations(df_copy, target_column)

        self.preparation_history.append(preparation_info)

        if self.verbose:
            logger.info(
                "ML preparation completed: strategy=%s, null_strategy=%s, shape %s → %s",
                strategy, null_strategy, preparation_info["original_shape"], preparation_info["final_shape"]
            )

        return df_copy, preparation_info

    # ------------------------- Null Handling -------------------------

    def _handle_nulls(
        self,
        df: pd.DataFrame,
        null_strategy: str,
        target_column: Optional[str] = None
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:

        out = df.copy()
        info: Dict[str, Any] = {"strategy": null_strategy}

        if null_strategy == "preserve":
            info["action"] = "preserved_for_ml_pipeline"
            info["null_columns"] = out.isnull().sum().to_dict()

        elif null_strategy == "drop":
            initial = len(out)
            out = out.dropna()
            dropped = initial - len(out)
            info.update({
                "action": f"dropped_{dropped}_rows_with_nulls",
                "rows_dropped": int(dropped),
                "rows_remaining": int(len(out)),
            })

        elif null_strategy == "mark":
            added = []
            for col in out.columns:
                if col != target_column and out[col].isnull().any():
                    ind = f"{col}_was_missing"
                    out[ind] = out[col].isnull().astype("int8")  # CHG: kleine Indikator-Dtype
                    added.append(ind)
            info.update({
                "action": f"added_{len(added)}_null_indicators",
                "null_indicator_columns": added,
            })

        elif null_strategy == "impute":
            info["action"] = "imputed_missing_values"
            info["imputation_summary"] = self._perform_imputation(out, target_column)

        elif null_strategy == "smart_drop":
            initial_shape = out.shape
            ratios = out.isnull().sum() / len(out)
            cols_to_drop = [c for c, r in ratios.items() if r > 0.7 and c != target_column]
            if cols_to_drop:
                out = out.drop(columns=cols_to_drop)
            out = out.dropna()
            info.update({
                "action": "smart_drop_columns_and_rows",
                "columns_dropped": cols_to_drop,
                "shape_change": f"{initial_shape} → {out.shape}",
            })

        return out, info

    def _perform_imputation(self, df: pd.DataFrame, target_column: Optional[str] = None) -> Dict[str, Any]:
        """
        Imputation nach Spaltentyp:
        - numerisch: Median
        - kategorial (object/category): Modus, sonst 'UNKNOWN'
        """
        out = df.copy()
        summary: Dict[str, Any] = {}

        num_cols = out.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = out.select_dtypes(include=["object", "category"]).columns.tolist()

        if target_column:
            num_cols = [c for c in num_cols if c != target_column]
            cat_cols = [c for c in cat_cols if c != target_column]

        # numerisch
        for col in num_cols:
            if out[col].isnull().any():
                n = int(out[col].isnull().sum())
                med = out[col].median()
                out[col] = out[col].fillna(med)
                summary[col] = {"type": "numeric", "method": "median", "value_used": float(med), "nulls_filled": n}

        # kategorial
        for col in cat_cols:
            if out[col].isnull().any():
                n = int(out[col].isnull().sum())
                mode = out[col].mode()
                if len(mode) > 0:
                    fill = mode.iat[0]
                    method = "mode"
                else:
                    fill = "UNKNOWN"
                    method = "constant"
                out[col] = out[col].fillna(fill)
                summary[col] = {"type": "categorical", "method": method, "value_used": fill, "nulls_filled": n}

        # in-place update des aufrufenden Frames gewollt
        df[:] = out
        return summary

    # ------------------------- Strategie/Optimierung -------------------------

    def _apply_ml_strategy(
        self,
        df: pd.DataFrame,
        strategy: str,
        target_column: Optional[str] = None
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:

        out = df.copy()
        info: Dict[str, Any] = {"strategy": strategy}

        if strategy == "preserve":
            info["actions"] = ["data_preserved"]

        elif strategy == "minimal":
            info["actions"] = ["data_types_optimized"]
            info["optimization_info"] = self._optimize_data_types(out)

        elif strategy == "full":
            actions = []

            opt = self._optimize_data_types(out)
            actions.append("data_types_optimized")

            feat = self._analyze_features_for_ml(out, target_column)
            actions.append("feature_analysis_completed")

            recs = self._generate_detailed_ml_recommendations(out, target_column)
            actions.append("ml_recommendations_generated")

            info.update({
                "actions": actions,
                "optimization_info": opt,
                "feature_analysis": feat,
                "ml_recommendations": recs,
            })

        return out, info

    def _optimize_data_types(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Robuste Dtype-Optimierung:
        - Integers/Float: `pd.to_numeric(..., downcast=...)`
        - Strings mit niedriger Kardinalität → category
        - Speichergewinn exakt via `memory_usage(deep=True)`
        """
        optimization_info: Dict[str, Any] = {
            "original_dtypes": df.dtypes.astype(str).to_dict(),
            "optimizations": {},
        }

        mem_before = int(df.memory_usage(deep=True).sum())  # NEW

        for col in df.columns:
            s = df[col]

            # Integers (inkl. pandas nullable Int*): downcast
            if pdt.is_integer_dtype(s):
                down = pd.to_numeric(s, downcast="integer")
                if down.dtype != s.dtype:
                    df[col] = down
                    optimization_info["optimizations"][col] = f"{s.dtype} → {down.dtype}"

            # Floats: downcast to float32 wenn sinnvoll (keine strengen Allclose-Scans)
            elif pdt.is_float_dtype(s):
                down = pd.to_numeric(s, downcast="float")
                if down.dtype != s.dtype:
                    df[col] = down
                    optimization_info["optimizations"][col] = f"{s.dtype} → {down.dtype}"

            # Objekte mit niedriger Kardinalität → category
            elif pdt.is_object_dtype(s):
                if len(s) > 0:
                    nunique = s.nunique(dropna=True)
                    ratio = nunique / len(s)
                    if nunique > 2 and ratio < 0.1:
                        df[col] = s.astype("category")
                        optimization_info["optimizations"][col] = "object → category"

        mem_after = int(df.memory_usage(deep=True).sum())  # NEW
        optimization_info["final_dtypes"] = df.dtypes.astype(str).to_dict()
        optimization_info["memory_saved"] = {
            "original_memory_bytes": mem_before,
            "final_memory_bytes": mem_after,
            "memory_saved_bytes": mem_before - mem_after,
            "memory_saved_percentage": ((mem_before - mem_after) / mem_before * 100) if mem_before > 0 else 0.0,
        }
        return optimization_info

    # ------------------------- Analysen & Empfehlungen -------------------------

    def _analyze_features_for_ml(self, df: pd.DataFrame, target_column: Optional[str] = None) -> Dict[str, Any]:
        analysis: Dict[str, Any] = {
            "total_features": len(df.columns),
            "numeric_features": [],
            "categorical_features": [],
            "high_cardinality_features": [],
            "low_variance_features": [],
            "features_with_nulls": [],
        }

        features = [c for c in df.columns if c != target_column]

        for col in features:
            s = df[col]
            if pdt.is_numeric_dtype(s):
                analysis["numeric_features"].append(col)
                try:
                    if s.var() < 0.01:
                        analysis["low_variance_features"].append(col)
                except Exception:
                    pass
            else:
                analysis["categorical_features"].append(col)
                try:
                    ratio = s.nunique(dropna=True) / len(s) if len(s) else 0
                    if ratio > 0.8:
                        analysis["high_cardinality_features"].append(col)
                except Exception:
                    pass

            if s.isnull().any():
                analysis["features_with_nulls"].append({
                    "column": col,
                    "null_percentage": (s.isnull().sum() / len(s) * 100) if len(s) else 0.0,
                })

        if target_column and target_column in df.columns:
            analysis["target_analysis"] = self._analyze_target_column(df[target_column])

        return analysis

    def _analyze_target_column(self, target_series: pd.Series) -> Dict[str, Any]:
        analysis: Dict[str, Any] = {
            "column_name": target_series.name,
            "dtype": str(target_series.dtype),
            "null_count": int(target_series.isnull().sum()),
            "unique_values": int(target_series.nunique()),
        }

        if pdt.is_numeric_dtype(target_series):
            uniq = int(target_series.nunique())
            if uniq <= 10:
                analysis["suggested_task_type"] = "classification"
                analysis["reason"] = f"Numeric with {uniq} unique values (likely discrete classes)"
            else:
                analysis["suggested_task_type"] = "regression"
                analysis["reason"] = f"Numeric with {uniq} unique values (continuous)"
        else:
            analysis["suggested_task_type"] = "classification"
            analysis["reason"] = "Categorical target variable"

        if analysis["suggested_task_type"] == "classification":
            counts = target_series.value_counts(dropna=False)
            analysis["class_distribution"] = {str(k): int(v) for k, v in counts.to_dict().items()}
            if len(counts) > 1:
                analysis["is_balanced"] = (counts.max() / counts.min()) < 3
            else:
                analysis["is_balanced"] = True

        return analysis

    def _generate_ml_recommendations(self, df: pd.DataFrame, target_column: Optional[str] = None) -> List[str]:
        recs: List[str] = []

        cats = df.select_dtypes(include=["object", "category"]).columns.tolist()
        if target_column in cats:
            cats.remove(target_column)
        if cats:
            recs.append(f"Consider encoding {len(cats)} categorical columns (one-hot or target encoding)")

        nums = df.select_dtypes(include=[np.number]).columns.tolist()
        if target_column in nums:
            nums.remove(target_column)
        if nums:
            recs.append(f"Consider scaling {len(nums)} numeric columns (StandardScaler or RobustScaler)")

        null_cols = df.isnull().sum()
        null_cols = null_cols[null_cols > 0]
        if len(null_cols) > 0:
            recs.append(f"Handle missing values in {len(null_cols)} columns before ML training")

        return recs

    def _generate_detailed_ml_recommendations(self, df: pd.DataFrame, target_column: Optional[str] = None) -> Dict[str, Any]:
        recommendations = {
            "preprocessing_steps": [],
            "feature_engineering": [],
            "model_suggestions": [],
            "validation_strategy": [],
        }

        cats = df.select_dtypes(include=["object", "category"]).columns.tolist()
        nums = df.select_dtypes(include=[np.number]).columns.tolist()

        if target_column:
            cats = [c for c in cats if c != target_column]
            nums = [c for c in nums if c != target_column]

        if cats:
            high = [c for c in cats if df[c].nunique(dropna=True) > 20]
            low = [c for c in cats if df[c].nunique(dropna=True) <= 20]
            if low:
                recommendations["preprocessing_steps"].append({
                    "step": "one_hot_encoding",
                    "columns": low,
                    "reason": "Low cardinality categorical columns suitable for one-hot encoding",
                })
            if high:
                recommendations["preprocessing_steps"].append({
                    "step": "target_encoding",
                    "columns": high,
                    "reason": "High cardinality categorical columns need target encoding or embedding",
                })

        if nums:
            recommendations["preprocessing_steps"].append({
                "step": "feature_scaling",
                "columns": nums,
                "methods": ["StandardScaler", "RobustScaler", "MinMaxScaler"],
                "reason": "Numeric features benefit from scaling for most ML algorithms",
            })

        date_cols = [c for c in df.columns if "date" in c.lower() or "time" in c.lower()]
        if date_cols:
            recommendations["feature_engineering"].append({
                "technique": "datetime_features",
                "columns": date_cols,
                "suggestions": ["extract year/month/day", "create time-based features", "calculate time differences"],
            })

        coord_cols = [c for c in df.columns if any(x in c.lower() for x in ["lat", "lng", "lon"])]
        if len(coord_cols) >= 2:
            recommendations["feature_engineering"].append({
                "technique": "geospatial_features",
                "columns": coord_cols,
                "suggestions": ["calculate distances", "create location clusters", "add geographic features"],
            })

        n = len(df)
        if target_column and target_column in df.columns:
            t = self._analyze_target_column(df[target_column])
            if t["suggested_task_type"] == "classification":
                if n < 1_000:
                    recommendations["model_suggestions"] += ["RandomForest", "SVM", "LogisticRegression"]
                elif n < 10_000:
                    recommendations["model_suggestions"] += ["XGBoost", "LightGBM", "RandomForest"]
                else:
                    recommendations["model_suggestions"] += ["XGBoost", "LightGBM", "Neural Networks"]
            else:
                if n < 1_000:
                    recommendations["model_suggestions"] += ["RandomForest", "SVR", "LinearRegression"]
                elif n < 10_000:
                    recommendations["model_suggestions"] += ["XGBoost", "LightGBM", "RandomForest"]
                else:
                    recommendations["model_suggestions"] += ["XGBoost", "LightGBM", "Neural Networks"]

        if n < 1_000:
            recommendations["validation_strategy"].append("Use Leave-One-Out or 10-fold cross-validation due to small dataset")
        elif n < 10_000:
            recommendations["validation_strategy"].append("Use 5-fold or 10-fold cross-validation")
        else:
            recommendations["validation_strategy"].append("Use train/validation/test split (70/15/15) with cross-validation")

        return recommendations

    # ------------------------- Scoring & History -------------------------

    def assess_ml_readiness(self, df: pd.DataFrame, target_column: Optional[str] = None) -> Dict[str, Any]:
        assessment: Dict[str, Any] = {
            "overall_score": 0,
            "readiness_level": "not_ready",
            "blocking_issues": [],
            "recommendations": [],
            "detailed_scores": {},
        }

        total_nulls = int(df.isnull().sum().sum())
        null_pct = (total_nulls / (len(df) * max(1, len(df.columns)))) * 100 if len(df) else 0.0

        # 1) Data Quality
        if null_pct == 0:
            dq = 25
        elif null_pct < 5:
            dq = 20
        elif null_pct < 15:
            dq = 15
        elif null_pct < 30:
            dq = 10
        else:
            dq = 0
            assessment["blocking_issues"].append(f"High null percentage: {null_pct:.1f}%")
        assessment["detailed_scores"]["data_quality"] = dq

        # 2) Data Size
        n = len(df)
        if n >= 10_000:
            ds = 25
        elif n >= 1_000:
            ds = 20
        elif n >= 100:
            ds = 15
        else:
            ds = 5
            assessment["blocking_issues"].append(f"Very small dataset: {n} rows")
        assessment["detailed_scores"]["data_size"] = ds

        # 3) Feature Quality
        num_cnt = len(df.select_dtypes(include=[np.number]).columns)
        cat_cnt = len(df.select_dtypes(include=["object", "category"]).columns)
        tot = num_cnt + cat_cnt - (1 if (target_column and target_column in df.columns) else 0)

        if tot >= 5:
            fq = 25
        elif tot >= 3:
            fq = 20
        elif tot >= 1:
            fq = 10
        else:
            fq = 0
            assessment["blocking_issues"].append("No usable features found")

        penalty = 0
        for col in df.select_dtypes(include=["object"]).columns:
            if col != target_column:
                try:
                    ratio = df[col].nunique(dropna=True) / len(df) if len(df) else 0
                    if ratio > 0.8:
                        penalty += 5
                except Exception:
                    pass
        fq = max(0, fq - penalty)
        assessment["detailed_scores"]["feature_quality"] = fq

        # 4) Target Quality
        if target_column:
            if target_column in df.columns:
                tnull = int(df[target_column].isnull().sum())
                if tnull == 0:
                    tq = 25
                elif tnull < len(df) * 0.05:
                    tq = 20
                elif tnull < len(df) * 0.15:
                    tq = 15
                else:
                    tq = 0
                    assessment["blocking_issues"].append(f'Target column has {tnull} null values')
            else:
                tq = 0
                assessment["blocking_issues"].append(f'Target column "{target_column}" not found')
        else:
            tq = 25
        assessment["detailed_scores"]["target_quality"] = tq

        assessment["overall_score"] = dq + ds + fq + tq

        if assessment["overall_score"] >= 80:
            assessment["readiness_level"] = "ready"
        elif assessment["overall_score"] >= 60:
            assessment["readiness_level"] = "mostly_ready"
        elif assessment["overall_score"] >= 40:
            assessment["readiness_level"] = "needs_work"
        else:
            assessment["readiness_level"] = "not_ready"

        if dq < 20:
            assessment["recommendations"].append("Clean missing values and outliers")
        if ds < 20:
            assessment["recommendations"].append("Consider collecting more data or using data augmentation")
        if fq < 20:
            assessment["recommendations"].append("Perform feature engineering or collect additional features")
        if tq < 20 and target_column:
            assessment["recommendations"].append("Address issues with target column")

        return assessment

    def get_preparation_history(self) -> List[Dict[str, Any]]:
        return self.preparation_history.copy()

    def get_preparation_stats(self) -> Dict[str, Any]:
        if not self.preparation_history:
            return {"total_preparations": 0}

        strategies = [p["strategy"] for p in self.preparation_history]
        null_strats = [p["null_strategy"] for p in self.preparation_history]

        return {
            "total_preparations": len(self.preparation_history),
            "strategies_used": {s: strategies.count(s) for s in set(strategies)},
            "null_strategies_used": {s: null_strats.count(s) for s in set(null_strats)},
            "avg_shape_reduction": self._calculate_avg_shape_reduction(),
            "most_common_recommendations": self._get_most_common_recommendations(),
        }

    def _calculate_avg_shape_reduction(self) -> Dict[str, float]:
        if not self.preparation_history:
            return {"avg_rows_reduction_percent": 0.0, "avg_columns_reduction_percent": 0.0}

        tr, tc = 0.0, 0.0
        for p in self.preparation_history:
            (r0, c0) = p["original_shape"]
            (r1, c1) = p["final_shape"]
            tr += ((r0 - r1) / r0 * 100.0) if r0 else 0.0
            tc += ((c0 - c1) / c0 * 100.0) if c0 else 0.0

        n = len(self.preparation_history)
        return {"avg_rows_reduction_percent": tr / n, "avg_columns_reduction_percent": tc / n}

    def _get_most_common_recommendations(self) -> List[str]:
        allrecs: List[str] = []
        for p in self.preparation_history:
            allrecs.extend(p.get("recommendations", []))
        counts: Dict[str, int] = {}
        for r in allrecs:
            counts[r] = counts.get(r, 0) + 1
        return [r for (r, _) in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]]
