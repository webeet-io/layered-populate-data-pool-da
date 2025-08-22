# -*- coding: utf-8 -*-
"""
BerlinDataValidator - Spezialisiert auf Berlin-spezifische Datenvalidierung
Einzelne Verantwortlichkeit: Domain-spezifische Validierungsregeln für Berlin Immobilien-App
"""

import re
import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime
from .utils import count_true

import pandas as pd

logger = logging.getLogger(__name__)


class BerlinDataValidator:
    """
    Spezialisierte Klasse für Berlin-spezifische Datenvalidierung
    
    Verantwortlichkeiten:
    - Berlin-Koordinaten validieren
    - Datum-Plausibilität prüfen
    - Email-Format validieren
    - Domain-spezifische Geschäftsregeln prüfen
    """
    
    def __init__(self, verbose: bool = True):
        """
        Initialize BerlinDataValidator
        
        Args:
            verbose: Enable detailed logging
        """
        self.verbose = verbose
        
        # Berlin-spezifische Grenzen
        self.berlin_bounds = {
            'lat_min': 52.0,
            'lat_max': 53.0,
            'lng_min': 12.5,
            'lng_max': 14.0
        }
        
        # Date patterns for validation
        self.date_patterns = [
            (r'\d{4}-\d{2}-\d{2}', '%Y-%m-%d'),      # 2024-01-01
            (r'\d{2}\.\d{2}\.\d{4}', '%d.%m.%Y'),    # 01.01.2024
            (r'\d{2}/\d{2}/\d{4}', '%d/%m/%Y'),      # 01/01/2024
        ]
        
        self.validation_history: List[Dict[str, Any]] = []
    
    def validate_berlin_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Comprehensive validation for Berlin-specific data
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Validation report dictionary
        """
        issues = []
        validation_details = {}
        
        # 1. DateTime validation
        date_validation = self._validate_datetime_columns(df)
        issues.extend(date_validation['issues'])
        validation_details['datetime_validation'] = date_validation
        
        # 2. Coordinate validation
        coord_validation = self._validate_coordinates(df)
        issues.extend(coord_validation['issues'])
        validation_details['coordinate_validation'] = coord_validation
        
        # 3. Email format validation
        email_validation = self._validate_email_formats(df)
        issues.extend(email_validation['issues'])
        validation_details['email_validation'] = email_validation
        
        # 4. Berlin-specific business rules
        business_validation = self._validate_berlin_business_rules(df)
        issues.extend(business_validation['issues'])
        validation_details['business_validation'] = business_validation
        
        # Create final validation report
        report = {
            'passed': len(issues) == 0,
            'total_issues': len(issues),
            'issues': issues,
            'validation_details': validation_details,
            'data_shape': df.shape,
            'validation_timestamp': datetime.now(),
            'summary': self._create_validation_summary(validation_details)
        }
        
        # Store in history
        self.validation_history.append(report)
        
        if self.verbose:
            logger.info(f"Validation completed: {len(issues)} issues found")
            if issues:
                logger.warning(f"Issues: {issues[:3]}{'...' if len(issues) > 3 else ''}")
        
        return report
    
    def _validate_datetime_columns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate datetime columns for Berlin data context"""
        issues = []
        date_columns = self._detect_date_columns(df)
        invalid_dates_summary = {}
        future_dates_summary = {}
        
        for col in date_columns:
            try:
                # Try to parse dates
                parsed_dates = pd.to_datetime(df[col], errors='coerce')
                
                # Check for invalid dates
                invalid_count = parsed_dates.isna().astype('int64').sum()
                total_count = len(df[col].dropna())
                
                if total_count > 0:
                    invalid_ratio = invalid_count / total_count
                    if invalid_ratio > 0.5:  # More than 50% invalid
                        issues.append(f"Column '{col}': {invalid_count}/{total_count} ({invalid_ratio:.1%}) invalid dates")
                        invalid_dates_summary[col] = {'count': invalid_count, 'ratio': invalid_ratio}
                
                # Check for future dates (potential webscraping errors)
                valid_dates = parsed_dates.dropna()
                if len(valid_dates) > 0:
                    future_count = (valid_dates > pd.Timestamp.now()).sum()
                    if future_count > 0:
                        issues.append(f"Column '{col}': {future_count} dates in future")
                        future_dates_summary[col] = future_count
                
                # Check for unreasonably old dates (before 1900)
                very_old = (valid_dates < pd.Timestamp('1900-01-01')).sum()
                if very_old > 0:
                    issues.append(f"Column '{col}': {very_old} dates before 1900")
                        
            except Exception as e:
                issues.append(f"Column '{col}': Cannot parse as datetime - {str(e)}")
        
        return {
            'issues': issues,
            'date_columns_found': date_columns,
            'invalid_dates_summary': invalid_dates_summary,
            'future_dates_summary': future_dates_summary,
            'columns_checked': len(date_columns)
        }
    
    def _validate_coordinates(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate geographic coordinates for Berlin area"""
        issues = []
        coord_columns = self._detect_coordinate_columns(df)
        out_of_bounds_summary = {}
        for col in coord_columns:
            s = pd.to_numeric(df[col], errors='coerce')  # <- robust gegen Strings
        if 'lat' in col.lower():
            out_of_range = count_true((s < self.berlin_bounds['lat_min']) | (s > self.berlin_bounds['lat_max']))
            total_valid = count_true(s.notna())
            if out_of_range > 0 and total_valid > 0:
                issues.append(f"Column '{col}': {out_of_range}/{total_valid} coordinates outside Berlin latitude range")
                out_of_bounds_summary[col] = {
                    'out_of_bounds': out_of_range,
                    'total': total_valid,
                    'expected_range': f"{self.berlin_bounds['lat_min']}-{self.berlin_bounds['lat_max']}"
                }
        if any(x in col.lower() for x in ['lng', 'lon']):
            out_of_range = count_true((s < self.berlin_bounds['lng_min']) | (s > self.berlin_bounds['lng_max']))
            total_valid = count_true(s.notna())
            if out_of_range > 0 and total_valid > 0:
                issues.append(f"Column '{col}': {out_of_range}/{total_valid} coordinates outside Berlin longitude range")
                out_of_bounds_summary[col] = {
                    'out_of_bounds': out_of_range,
                    'total': total_valid,
                    'expected_range': f"{self.berlin_bounds['lng_min']}-{self.berlin_bounds['lng_max']}"
                }

        
        return {
            'issues': issues,
            'coordinate_columns_found': coord_columns,
            'out_of_bounds_summary': out_of_bounds_summary,
            'berlin_bounds': self.berlin_bounds,
            'columns_checked': len(coord_columns)
        }
    
    def _validate_email_formats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate email format in email columns"""
        issues = []
        email_columns = self._detect_email_columns(df)
        email_validation_summary = {}
        
        # Email regex pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        for col in email_columns:
            if df[col].dtype == 'object':
                non_null_emails = df[col].dropna()
                if len(non_null_emails) > 0:
                    valid_emails = count_true(non_null_emails.astype(str).str.match(email_pattern))
                    total_emails = len(non_null_emails)
                    
                    if total_emails > 0:
                        valid_ratio = valid_emails / total_emails
                        if valid_ratio < 0.8:  # Less than 80% valid
                            issues.append(f"Column '{col}': Only {valid_emails}/{total_emails} ({valid_ratio:.1%}) valid email formats")
                            email_validation_summary[col] = {
                                'valid': valid_emails,
                                'total': total_emails,
                                'valid_ratio': valid_ratio
                            }
        
        return {
            'issues': issues,
            'email_columns_found': email_columns,
            'email_validation_summary': email_validation_summary,
            'columns_checked': len(email_columns)
        }
    def _detect_date_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Heuristik: Spaltennamen oder Werte-Muster deuten auf Datum
        """
        date_cols = []
        name_hints = ("date", "datum", "zeit", "time", "created", "updated")
        value_regex = r"(?:\d{4}-\d{2}-\d{2})|(?:\d{2}[./]\d{2}[./]\d{4})"

        for col in df.columns:
            name = str(col).lower()
            if any(h in name for h in name_hints):
                date_cols.append(col)
                continue
            # Musterprüfung auf Stichprobe
            sample = df[col].dropna().astype(str).head(10)
            if len(sample) and sample.str.contains(value_regex, regex=True).any():
                date_cols.append(col)

        # Duplikate vermeiden (falls doppelt gezählt)
        return list(dict.fromkeys(date_cols))


    def _detect_coordinate_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Heuristik: lat/lon/lng im Spaltennamen
        """
        coord_hints = ("lat", "latitude", "lon", "lng", "longitude")
        cols = [c for c in df.columns if any(h in c.lower() for h in coord_hints)]
        return cols


    def _detect_email_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Heuristik: E-Mail durch Name oder '@' in Stichprobe
        """
        email_cols = []
        name_hints = ("email", "e_mail", "mail")
        for col in df.columns:
            name = str(col).lower()
            if any(h in name for h in name_hints):
                email_cols.append(col)
                continue
            sample = df[col].dropna().astype(str).head(10)
            if len(sample) and sample.str.contains(r"@", regex=True).any():
                email_cols.append(col)
        return list(dict.fromkeys(email_cols))

    def get_validation_stats(self) -> Dict[str, Any]:
        """
        Liefert kompakte Statistik über alle bisherigen Validierungsläufe.
        """
        if not getattr(self, "validation_history", None):
            return {
                "total_runs": 0,
                "total_issues": 0,
                "last_run_passed": None,
                "last_run_timestamp": None,
            }

        total_runs = len(self.validation_history)
        total_issues = sum(r.get("total_issues", 0) for r in self.validation_history)
        last = self.validation_history[-1]
        last_ts = last.get("validation_timestamp")
        # falls der Zeitstempel ein datetime ist -> in ISO konvertieren (robust für JSON)
        try:
            from datetime import datetime
            if isinstance(last_ts, datetime):
                last_ts = last_ts.isoformat()
        except Exception:
            pass

        return {
            "total_runs": total_runs,
            "total_issues": total_issues,
            "last_run_passed": last.get("passed"),
            "last_run_timestamp": last_ts,
        }

    def _validate_berlin_business_rules(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate Berlin-specific business rules"""
        issues = []
        business_checks = {}
        
        # Check for postal code validation (Berlin: 10xxx-14xxx)
        postal_columns = [col for col in df.columns if any(x in col.lower() 
                         for x in ['plz', 'postal', 'zip', 'postcode'])]
        
        for col in postal_columns:
            if df[col].dtype in ['object', 'int64', 'float64']:
                # Convert to string for pattern matching
                postal_codes = df[col].astype(str).str.strip()
                
                # Berlin postal codes: 10xxx to 14xxx
                berlin_pattern = r'^1[0-4]\d{3}$'
                valid_postal = count_true(postal_codes.str.match(berlin_pattern))
                total_postal = count_true(postal_codes.notna())
                
                if total_postal > 0:
                    valid_ratio = valid_postal / total_postal
                    if valid_ratio < 0.9:  # Less than 90% valid for Berlin
                        issues.append(
                            f"Column '{col}': Only {valid_postal}/{total_postal} ({valid_ratio:.1%}) valid Berlin postal codes"
                        )
                    business_checks[col] = {
                        'valid_postal': valid_postal,
                        'total_postal': total_postal,
                        'valid_ratio': valid_ratio
                    }

        # Optional: Preis-/Flächen-Plausibilität (falls Spalten vorhanden)
        price_cols = [c for c in df.columns if any(x in c.lower() for x in ['price', 'kaltmiete', 'warmmiete', 'kaufpreis'])]
        area_cols  = [c for c in df.columns if any(x in c.lower() for x in ['area', 'qm', 'm2', 'm²', 'wohnflaeche', 'wohnfläche'])]

        for col in price_cols:
            s = pd.to_numeric(df[col], errors='coerce')
            if s.notna().any():
                neg = count_true(s < 0)
                if neg:
                    issues.append(f"Column '{col}': {neg} negative price values")
        for col in area_cols:
            s = pd.to_numeric(df[col], errors='coerce')
            if s.notna().any():
                nonpos = count_true(s < 0)
                if nonpos:
                    issues.append(f"Column '{col}': {nonpos} non-positive area values")

        return {
            'issues': issues,
            'business_checks': business_checks,
            'postal_columns_checked': postal_columns,
            'price_columns_checked': price_cols,
            'area_columns_checked': area_cols
        }
    def _create_validation_summary(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Erzeuge eine kompakte Zusammenfassung aus den Detailreports.
        Defensive Implementierung: alle Keys sind optional.
        """
        dt = details.get("datetime_validation", {}) or {}
        co = details.get("coordinate_validation", {}) or {}
        em = details.get("email_validation", {}) or {}
        bu = details.get("business_validation", {}) or {}

        # Datetime
        dt_invalid_cols = list((dt.get("invalid_dates_summary") or {}).keys())
        dt_future_cols = list((dt.get("future_dates_summary") or {}).keys())
        dt_summary = {
            "columns_checked": dt.get("columns_checked", 0),
            "date_columns_found": len(dt.get("date_columns_found", []) or []),
            "invalid_date_columns": dt_invalid_cols,
            "future_date_columns": dt_future_cols,
        }

        # Coordinates
        co_out_cols = list((co.get("out_of_bounds_summary") or {}).keys())
        co_summary = {
            "columns_checked": co.get("columns_checked", 0),
            "coordinate_columns_found": len(co.get("coordinate_columns_found", []) or []),
            "out_of_bounds_columns": co_out_cols,
            "bounds": co.get("berlin_bounds"),
        }

        # Emails
        em_low_cols = list((em.get("email_validation_summary") or {}).keys())
        em_summary = {
            "columns_checked": em.get("columns_checked", 0),
            "email_columns_found": len(em.get("email_columns_found", []) or []),
            "low_valid_ratio_columns": em_low_cols,
        }

        # Business
        bu_summary = {
            "postal_columns_checked": len(bu.get("postal_columns_checked", []) or []),
            "price_columns_checked": len(bu.get("price_columns_checked", []) or []),
            "area_columns_checked": len(bu.get("area_columns_checked", []) or []),
            "issues_in_business_checks": len(bu.get("issues", []) or []),
        }

        # Overall
        overall_issues = sum([
            len(dt.get("issues", []) or []),
            len(co.get("issues", []) or []),
            len(em.get("issues", []) or []),
            len(bu.get("issues", []) or []),
        ])

        return {
            "datetime": dt_summary,
            "coordinates": co_summary,
            "emails": em_summary,
            "business": bu_summary,
            "overall_issues": overall_issues,
        }

