# -*- coding: utf-8 -*-
"""
WebscrapingDataCleaner - Spezialisiert auf Webscraping-Datenbereinigung
Einzelne Verantwortlichkeit: Webscraping-Artefakte erkennen und bereinigen
"""

import logging
from typing import Dict, List, Any, Set, Tuple

import pandas as pd
import numpy as np

from .utils import count_true

logger = logging.getLogger(__name__)


class WebscrapingDataCleaner:
    """
    Detects and cleans common web-scraping artifacts.

    - Treats a configurable set of string tokens as null (e.g., '', 'N/A', 'null', ...).
    - Per-column artifact counting before replacement.
    - Replaces artifacts with NaN, trims strings, restores object downcasting via `infer_objects`.
    - Keeps a `cleaning_history` and exposes summary stats.
    """
    
    def __init__(self, custom_null_values: List[str] = None, verbose: bool = True):
        """
        Initialize WebscrapingDataCleaner
        
        Args:
            custom_null_values: Additional values to treat as null
            verbose: Enable detailed logging
        """
        self.verbose = verbose
        
        # Standard webscraping null artifacts
        self.standard_nulls = [
            '', 'N/A', 'n/a', 'null', 'NULL', 'None', 'NONE',
            'undefined', 'UNDEFINED', '-', '--', '---', 
            'nan', 'NaN', 'NAN', 'nil', 'NIL'
        ]
        
        # Add custom null values if provided
        if custom_null_values:
            self.standard_nulls.extend(custom_null_values)
        
        # Remove duplicates while preserving order
        self.null_values = list(dict.fromkeys(self.standard_nulls))
        
        self.cleaning_history: List[Dict[str, Any]] = []
    
    def clean_webscraping_artifacts(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Clean webscraping artifacts from DataFrame
        
        Args:
            df: Input DataFrame with potential webscraping artifacts
            
        Returns:
            Tuple[pd.DataFrame, Dict]: (cleaned_df, cleaning_report)
        """
        df_copy = df.copy()
        
        # Track artifacts found
        artifacts_found = {}
        total_artifacts_cleaned = 0
        
        # Process each column
        for col in df_copy.columns:
            if df_copy[col].dtype == 'object':
                artifacts_in_col = self._clean_column_artifacts(df_copy, col)
                if artifacts_in_col['artifacts_found']:
                    artifacts_found[col] = artifacts_in_col['artifacts_found']
                    total_artifacts_cleaned += artifacts_in_col['total_cleaned']
        
        # Create cleaning report
        report = {
            'artifacts_found': artifacts_found,
            'total_artifacts_cleaned': total_artifacts_cleaned,
            'affected_columns': list(artifacts_found.keys()),
            'columns_processed': len([col for col in df_copy.columns if df_copy[col].dtype == 'object']),
            'null_values_used': self.null_values.copy()
        }
        
        # Store in history
        self.cleaning_history.append(report)
        
        if self.verbose:
            logger.info(f"Cleaned {total_artifacts_cleaned} webscraping artifacts")
            logger.info(f"Affected columns: {len(artifacts_found)}")
        
        return df_copy, report
    
    def _clean_column_artifacts(self, df: pd.DataFrame, column: str) -> Dict[str, Any]:
        """
        Clean artifacts from a single column
        
        Args:
            df: DataFrame to modify in place
            column: Column name to clean
            
        Returns:
            Dictionary with cleaning statistics for this column
        """
        artifacts_found = {}
        total_cleaned = 0
        
        # Count each type of artifact before cleaning
        for null_val in self.null_values:
            if null_val == '':  # Handle empty string specially
                count = (df[column] == '').sum()
            else:
                count = (df[column] == null_val).sum()
            
            if count > 0:
                artifacts_found[null_val] = count
                total_cleaned += count
        
        # Replace all artifacts with NaN — danach explizit infer_objects()
        ser = df[column].replace(self.null_values, np.nan)

        # Clean whitespace; astype(str) kann 'nan' erzeugen → gleich abfangen
        ser = ser.astype(str).str.strip()
        ser = ser.replace({'nan': np.nan, '': np.nan})

        # Wichtig: altes Downcasting-Verhalten explizit herstellen
        ser = ser.infer_objects(copy=False)

        df[column] = ser

        
        return {
            'artifacts_found': artifacts_found,
            'total_cleaned': total_cleaned
        }
    
    def detect_potential_artifacts(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect potential artifacts without cleaning them
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Detection report
        """
        potential_artifacts = {}
        suspicious_patterns = {}
        
        for col in df.columns:
            if df[col].dtype == 'object':
                col_artifacts = {}
                col_patterns = []
                
                # Check for known null values
                for null_val in self.null_values:
                    count = (df[col] == null_val).sum()
                    if count > 0:
                        col_artifacts[null_val] = count
                
                # Check for suspicious patterns
                if len(df[col].dropna()) > 0:
                    unique_values = df[col].value_counts()
                    
                    # Single character values (suspicious)
                    single_chars = [val for val in unique_values.index 
                                  if isinstance(val, str) and len(val) == 1 and val.isalnum()]
                    if single_chars:
                        col_patterns.append(f"Single characters: {single_chars[:5]}")
                    
                    # Repeated patterns
                    repeated_patterns = [val for val, count in unique_values.items()
                                       if isinstance(val, str) and len(val) <= 5 and count > len(df) * 0.05]
                    if repeated_patterns:
                        col_patterns.append(f"Repeated short values: {repeated_patterns[:5]}")
                    
                    # HTML/XML tags
                    html_like = [val for val in unique_values.index[:10] 
                               if isinstance(val, str) and ('<' in val and '>' in val)]
                    if html_like:
                        col_patterns.append(f"HTML-like content: {len(html_like)} values")
                
                if col_artifacts:
                    potential_artifacts[col] = col_artifacts
                if col_patterns:
                    suspicious_patterns[col] = col_patterns
        
        return {
            'potential_null_artifacts': potential_artifacts,
            'suspicious_patterns': suspicious_patterns,
            'columns_with_artifacts': len(potential_artifacts),
            'columns_with_patterns': len(suspicious_patterns),
            'recommendation': self._get_cleaning_recommendations(potential_artifacts, suspicious_patterns)
        }
    
    def _get_cleaning_recommendations(self, artifacts: Dict, patterns: Dict) -> List[str]:
        """Generate cleaning recommendations based on detected issues"""
        recommendations = []
        
        if artifacts:
            total_artifacts = sum(sum(col_artifacts.values()) for col_artifacts in artifacts.values())
            recommendations.append(f"Found {total_artifacts} null-like artifacts that should be cleaned")
        
        if patterns:
            recommendations.append("Suspicious patterns detected - manual review recommended")
            
            for col, pattern_list in patterns.items():
                if any('HTML-like' in pattern for pattern in pattern_list):
                    recommendations.append(f"Column '{col}': Contains HTML tags - consider HTML parsing")
                if any('Single characters' in pattern for pattern in pattern_list):
                    recommendations.append(f"Column '{col}': Many single-character values - check data quality")
        
        if not artifacts and not patterns:
            recommendations.append("No obvious webscraping artifacts detected")
        
        return recommendations
    
    def add_custom_null_value(self, null_value: str):
        """
        Add a custom value to be treated as null
        
        Args:
            null_value: Value to add to null detection
        """
        if null_value not in self.null_values:
            self.null_values.append(null_value)
            if self.verbose:
                logger.info(f"Added custom null value: '{null_value}'")
    
    def remove_null_value(self, null_value: str):
        """
        Remove a value from null detection
        
        Args:
            null_value: Value to remove from null detection
        """
        if null_value in self.null_values:
            self.null_values.remove(null_value)
            if self.verbose:
                logger.info(f"Removed null value: '{null_value}'")
    
    def get_null_values(self) -> List[str]:
        """
        Get current list of values treated as null
        
        Returns:
            List of null values
        """
        return self.null_values.copy()
    
    def get_cleaning_history(self) -> List[Dict[str, Any]]:
        """
        Get cleaning history
        
        Returns:
            List of cleaning reports
        """
        return self.cleaning_history.copy()
    
    def get_cleaning_stats(self) -> Dict[str, Any]:
        """
        Get summary statistics from all cleaning operations
        
        Returns:
            Summary statistics
        """
        if not self.cleaning_history:
            return {'total_operations': 0}
        
        total_artifacts = sum(report['total_artifacts_cleaned'] for report in self.cleaning_history)
        total_columns = sum(len(report['affected_columns']) for report in self.cleaning_history)
        
        return {
            'total_operations': len(self.cleaning_history),
            'total_artifacts_cleaned': total_artifacts,
            'total_columns_affected': total_columns,
            'avg_artifacts_per_operation': total_artifacts / len(self.cleaning_history),
            'most_common_artifacts': self._get_most_common_artifacts()
        }
    
    def _get_most_common_artifacts(self) -> Dict[str, int]:
        """Get the most commonly found artifacts across all operations"""
        artifact_counts = {}
        
        for report in self.cleaning_history:
            for col_artifacts in report['artifacts_found'].values():
                for artifact, count in col_artifacts.items():
                    artifact_counts[artifact] = artifact_counts.get(artifact, 0) + count
        
        # Sort by frequency and return top 10
        sorted_artifacts = sorted(artifact_counts.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_artifacts[:10])