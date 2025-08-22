# -*- coding: utf-8 -*-
"""
ColumnStandardizer - Spezialisiert auf Spalten-Normalisierung
Einzelne Verantwortlichkeit: Spaltennamen standardisieren und bereinigen
"""

import re
import logging
from typing import List, Dict, Any, Tuple

import pandas as pd

logger = logging.getLogger(__name__)


class ColumnStandardizer:
    """
    Spezialisierte Klasse für Spalten-Standardisierung
    
    Verantwortlichkeiten:
    - Spaltennamen normalisieren
    - Duplikate handhaben
    - Standardisierungs-Historie verfolgen
    """
    
    def __init__(self, verbose: bool = True):
        """
        Initialize ColumnStandardizer
        
        Args:
            verbose: Enable detailed logging
        """
        self.verbose = verbose
        self.standardization_history: List[Dict[str, Any]] = []
    
    def standardize_columns(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Standardisiere Spaltennamen mit detailliertem Reporting
        
        Args:
            df: Input DataFrame
            
        Returns:
            Tuple[pd.DataFrame, Dict]: (processed_df, standardization_report)
        """
        df_copy = df.copy()
        original_columns = list(df.columns)
        
        # Step 1: Basic cleaning
        cleaned_columns = self._clean_column_names(original_columns)
        
        # Step 2: Handle duplicates
        final_columns = self._handle_duplicate_columns(cleaned_columns)
        
        # Apply new column names
        df_copy.columns = final_columns
        
        # Create report
        report = self._create_standardization_report(
            original_columns, 
            cleaned_columns, 
            final_columns
        )
        
        # Store in history
        self.standardization_history.append(report)
        
        if self.verbose:
            logger.info(f"Standardized {len(final_columns)} column names")
            logger.info(f"Made changes to {report['changes_made']} columns")
        
        return df_copy, report
    def _clean_column_names(self, columns: List[str]) -> List[str]:
        """
        Clean individual column names
        """
        cleaned = []
        umlaut_map = {
        "ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss",
        "Ä": "Ae", "Ö": "Oe", "Ü": "Ue",
        }

        for col in columns:
            # to string + trim
            col_str = str(col).strip()

            # replace German umlauts/ß BEFORE lowercasing/regex
            for k, v in umlaut_map.items():
                col_str = col_str.replace(k, v)

            # lowercase
            col_str = col_str.lower()

            # Replace special chars with underscore
            col_str = re.sub(r'[^\w\s]', '_', col_str)

            # Collapse spaces/underscores
            col_str = re.sub(r'\s+', '_', col_str)
            col_str = re.sub(r'_+', '_', col_str)

            # Trim underscores
            col_str = col_str.strip('_')

            if not col_str:
                col_str = 'unnamed_column'

            cleaned.append(col_str)

        return cleaned

    
    '''def _clean_column_names(self, columns: List[str]) -> List[str]:
        """
        Clean individual column names
        
        Args:
            columns: List of original column names
            
        Returns:
            List of cleaned column names
        """
        cleaned = []
        
        for col in columns:
            # Convert to string and strip
            col_str = str(col).strip().lower()
            
            # Replace special characters with underscores
            col_str = re.sub(r'[^\w\s]', '_', col_str)
            
            # Replace multiple spaces/underscores with single underscore
            col_str = re.sub(r'\s+', '_', col_str)
            col_str = re.sub(r'_+', '_', col_str)
            
            # Remove leading/trailing underscores
            col_str = col_str.strip('_')
            
            # Ensure not empty
            if not col_str:
                col_str = 'unnamed_column'
            
            cleaned.append(col_str)
        
        return cleaned'''
    
    def _handle_duplicate_columns(self, columns: List[str]) -> List[str]:
        """
        Handle duplicate column names by adding suffixes
        
        Args:
            columns: List of cleaned column names
            
        Returns:
            List of unique column names
        """
        seen = {}
        final_columns = []
        
        for col in columns:
            if col in seen:
                seen[col] += 1
                final_columns.append(f"{col}_{seen[col]}")
            else:
                seen[col] = 0
                final_columns.append(col)
        
        return final_columns
    
    def _create_standardization_report(self, 
                                     original: List[str], 
                                     cleaned: List[str], 
                                     final: List[str]) -> Dict[str, Any]:
        """
        Create detailed standardization report
        
        Args:
            original: Original column names
            cleaned: Cleaned column names
            final: Final column names with duplicates handled
            
        Returns:
            Standardization report dictionary
        """
        changes = []
        for i, (orig, clean, fin) in enumerate(zip(original, cleaned, final)):
            if orig != fin:
                changes.append({
                    'position': i,
                    'original': orig,
                    'cleaned': clean,
                    'final': fin,
                    'had_duplicates': clean != fin
                })
        
        duplicates_found = len([col for col in cleaned if cleaned.count(col) > 1])
        
        return {
            'original_columns': original,
            'cleaned_columns': cleaned,
            'final_columns': final,
            'changes_made': len(changes),
            'changes_detail': changes,
            'duplicates_handled': duplicates_found,
            'total_columns': len(final)
        }
    
    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get standardization history
        
        Returns:
            List of all standardization reports
        """
        return self.standardization_history.copy()
    
    def validate_column_names(self, columns: List[str]) -> Dict[str, Any]:
        """
        Validate column names for common issues
        
        Args:
            columns: List of column names to validate
            
        Returns:
            Validation report
        """
        issues = []
        
        # Check for problematic characters
        for i, col in enumerate(columns):
            if not isinstance(col, str):
                issues.append(f"Column {i}: Not a string type")
                continue
                
            if col.strip() != col:
                issues.append(f"Column '{col}': Has leading/trailing whitespace")
            
            if re.search(r'[^\w\s_]', col):
                issues.append(f"Column '{col}': Contains special characters")
            
            if col.upper() == col and len(col) > 3:
                issues.append(f"Column '{col}': All uppercase (consider lowercase)")
            
            if ' ' in col:
                issues.append(f"Column '{col}': Contains spaces")
        
        # Check for duplicates
        duplicates = [col for col in columns if columns.count(col) > 1]
        if duplicates:
            unique_duplicates = list(set(duplicates))
            for dup in unique_duplicates:
                count = columns.count(dup)
                issues.append(f"Column '{dup}': Appears {count} times")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'total_columns': len(columns),
            'duplicate_columns': len(set(duplicates)),
            'recommendations': self._get_column_recommendations(columns, issues)
        }
    
    def _get_column_recommendations(self, columns: List[str], issues: List[str]) -> List[str]:
        """Get recommendations for column improvements"""
        recommendations = []
        
        if any('special characters' in issue for issue in issues):
            recommendations.append("Use standardize_columns() to clean special characters")
        
        if any('spaces' in issue for issue in issues):
            recommendations.append("Replace spaces with underscores")
        
        if any('uppercase' in issue for issue in issues):
            recommendations.append("Consider using lowercase for better consistency")
        
        if any('Appears' in issue and 'times' in issue for issue in issues):
            recommendations.append("Resolve duplicate column names")
        
        return recommendations