# -*- coding: utf-8 -*-
"""
DataProcessor - Refactored mit Delegation zu spezialisierten Klassen
Hauptklasse orchestriert verschiedene Processing-Komponenten
"""

import logging
from typing import Any, Dict, List, Optional, Union

import pandas as pd

# Import der spezialisierten Komponenten
from .processing_metadata import ProcessingMetadata
from .column_standardizer import ColumnStandardizer
from .webscraping_cleaner import WebscrapingDataCleaner
from .berlin_data_validator import BerlinDataValidator
from .ml_data_preparer import MLDataPreparer
from .utils import count_true, col_null_counts

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Refactored DataProcessor - orchestriert spezialisierte Processing-Komponenten
    
    Architektur:
    - Delegation zu fokussierten Klassen statt einer Monolith-Klasse
    - Jede Komponente hat eine klare Verantwortlichkeit
    - Metadata-Management zentral koordiniert
    - Testbare, modulare Komponenten
    """

    def __init__(self, metadata: Optional[ProcessingMetadata] = None, verbose: bool = True):
        """
        Initialize DataProcessor with specialized components
        
        Args:
            metadata: ProcessingMetadata instance für Kontext-Tracking
            verbose: Enable detailed logging across all components
        """
        self.metadata = metadata or ProcessingMetadata(file_path="unknown")
        self.verbose = verbose
        
        # Initialize specialized components
        self.column_standardizer = ColumnStandardizer(verbose=verbose)
        self.webscraping_cleaner = WebscrapingDataCleaner(verbose=verbose)
        self.data_validator = BerlinDataValidator(verbose=verbose)
        self.ml_preparer = MLDataPreparer(verbose=verbose)
        
        if self.verbose:
            logger.info("DataProcessor initialized with specialized components")

    @classmethod
    def from_load_report(cls, load_report, file_path: str = None, verbose: bool = True) -> 'DataProcessor':
        """
        Factory method: Erstelle DataProcessor mit LoadReport
        
        Args:
            load_report: LoadReport object oder dict
            file_path: Optional override für file path
            verbose: Enable verbose logging
            
        Returns:
            DataProcessor instance mit ProcessingMetadata
        """
        metadata = ProcessingMetadata.from_load_report(load_report, file_path)
        return cls(metadata=metadata, verbose=verbose)

    @classmethod
    def with_metadata(cls, metadata: ProcessingMetadata, verbose: bool = True) -> 'DataProcessor':
        """
        Factory method: Erstelle DataProcessor mit bestehenden Metadaten
        
        Args:
            metadata: Bestehende ProcessingMetadata instance
            verbose: Enable verbose logging
            
        Returns:
            DataProcessor instance
        """
        return cls(metadata=metadata, verbose=verbose)

    def standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Delegiert zu ColumnStandardizer
        
        Args:
            df: DataFrame mit zu standardisierenden Spalten
            
        Returns:
            DataFrame mit standardisierten Spaltennamen
        """
        df_result, report = self.column_standardizer.standardize_columns(df)
        
        # Update metadata with standardization info
        self.metadata.add_processing_step('standardize_columns', report)
        
        if self.verbose:
            logger.info(f"Column standardization: {report['changes_made']} columns modified")
        
        return df_result

    def clean_webscraping_artifacts(self, df: pd.DataFrame, custom_null_values: List[str] = None) -> pd.DataFrame:
        """
        Delegiert zu WebscrapingDataCleaner
        
        Args:
            df: DataFrame mit potentiellen Webscraping-Artefakten
            custom_null_values: Zusätzliche Werte die als null behandelt werden sollen
            
        Returns:
            DataFrame mit bereinigten Webscraping-Artefakten
        """
        # Add custom null values if provided
        if custom_null_values:
            for null_val in custom_null_values:
                self.webscraping_cleaner.add_custom_null_value(null_val)
        
        df_result, report = self.webscraping_cleaner.clean_webscraping_artifacts(df)
        
        # Update metadata with cleaning info
        self.metadata.add_processing_step('clean_webscraping_artifacts', report)
        
        if self.verbose:
            logger.info(f"Webscraping cleanup: {report['total_artifacts_cleaned']} artifacts cleaned")
        
        return df_result

    def validate_berlin_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Delegiert zu BerlinDataValidator
        
        Args:
            df: DataFrame für Berlin-spezifische Validierung
            
        Returns:
            Validation report
        """
        validation_report = self.data_validator.validate_berlin_data(df)
        
        # Update metadata with validation results
        self.metadata.set_validation_results({
            'passed': validation_report['passed'],
            'total_issues': validation_report['total_issues'],
            'issues': validation_report['issues'],
            'validation_type': 'berlin_domain_specific'
        })
        
        self.metadata.add_processing_step('validate_berlin_data', {
            'validation_passed': validation_report['passed'],
            'issues_found': validation_report['total_issues']
        })
        
        # Add validation issues as warnings to metadata
        for issue in validation_report['issues']:
            self.metadata.add_warning(issue)
        
        if self.verbose:
            logger.info(f"Berlin data validation: {'PASSED' if validation_report['passed'] else 'FAILED'}")
            if not validation_report['passed']:
                logger.warning(f"Found {validation_report['total_issues']} validation issues")
        
        return validation_report

    def prepare_for_ml(self, 
                      df: pd.DataFrame, 
                      strategy: str = "preserve", 
                      null_strategy: str = "preserve",
                      target_column: Optional[str] = None) -> pd.DataFrame:
        """
        Delegiert zu MLDataPreparer
        
        Args:
            df: Input DataFrame
            strategy: ML preparation strategy ('preserve', 'minimal', 'full')
            null_strategy: How to handle nulls ('preserve', 'drop', 'mark', 'impute')
            target_column: Optional target column name
            
        Returns:
            DataFrame prepared for ML pipeline
        """
        df_result, report = self.ml_preparer.prepare_for_ml(df, strategy, null_strategy, target_column)
        
        # Update metadata with ML preparation info
        self.metadata.set_ml_preparation(strategy, null_strategy, report)
        self.metadata.add_processing_step('prepare_for_ml', {
            'strategy': strategy,
            'null_strategy': null_strategy,
            'target_column': target_column,
            'shape_change': f"{report['original_shape']} → {report['final_shape']}",
            'recommendations_count': len(report.get('recommendations', []))
        })
        if self.verbose:
            logger.info(f"ML preparation completed: {strategy} strategy, {null_strategy} null handling")
            
        return df_result, report
        
        
        

    def assess_ml_readiness(self, df: pd.DataFrame, target_column: Optional[str] = None) -> Dict[str, Any]:
        """
        Delegiert zu MLDataPreparer für ML-Readiness Assessment
        
        Args:
            df: DataFrame to assess
            target_column: Optional target column
            
        Returns:
            ML readiness assessment
        """
        assessment = self.ml_preparer.assess_ml_readiness(df, target_column)
        
        # Update metadata with assessment
        self.metadata.add_processing_step('assess_ml_readiness', {
            'overall_score': assessment['overall_score'],
            'readiness_level': assessment['readiness_level'],
            'blocking_issues': assessment['blocking_issues'],
            'target_column': target_column
        })
        
        if self.verbose:
            logger.info(f"ML readiness: {assessment['readiness_level']} (Score: {assessment['overall_score']}/100)")
        
        return assessment

    def detect_webscraping_artifacts(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Delegiert zu WebscrapingDataCleaner für Artefakt-Erkennung ohne Bereinigung
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Detection report
        """
        detection_report = self.webscraping_cleaner.detect_potential_artifacts(df)
        
        self.metadata.add_processing_step('detect_webscraping_artifacts', {
            'artifacts_detected': len(detection_report['potential_null_artifacts']),
            'patterns_detected': len(detection_report['suspicious_patterns']),
            'columns_with_issues': detection_report['columns_with_artifacts'] + detection_report['columns_with_patterns']
        })
        
        return detection_report

    def validate_column_names(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Delegiert zu ColumnStandardizer für Spaltennamen-Validierung
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Column validation report
        """
        validation_report = self.column_standardizer.validate_column_names(df.columns.tolist())
        
        self.metadata.add_processing_step('validate_column_names', {
            'validation_passed': validation_report['valid'],
            'issues_found': len(validation_report['issues']),
            'duplicate_columns': validation_report['duplicate_columns']
        })
        
        # Add column issues as warnings
        for issue in validation_report['issues']:
            self.metadata.add_warning(f"Column validation: {issue}")
        
        return validation_report

    # =================================================================
    # CONVENIENCE METHODS - Full Processing Pipelines
    # =================================================================

    def process_webscraping_data(self, df: pd.DataFrame, custom_null_values: List[str] = None) -> pd.DataFrame:
        """
        Complete pipeline for webscraping data processing
        
        Args:
            df: Raw webscraping DataFrame
            custom_null_values: Additional null values to clean
            
        Returns:
            Fully processed DataFrame
        """
        if self.verbose:
            logger.info("Starting complete webscraping data processing pipeline")
        
        # Step 1: Standardize columns
        df_processed = self.standardize_columns(df)
        
        # Step 2: Clean webscraping artifacts
        df_processed = self.clean_webscraping_artifacts(df_processed, custom_null_values)
        
        if self.verbose:
            logger.info("Webscraping data processing pipeline completed")
        
        return df_processed

    def process_berlin_real_estate_data(self, 
                                       df: pd.DataFrame, 
                                       custom_null_values: List[str] = None,
                                       ml_strategy: str = "minimal") -> pd.DataFrame:
        """
        Complete pipeline for Berlin real estate data
        
        Args:
            df: Raw real estate DataFrame
            custom_null_values: Additional null values to clean
            ml_strategy: ML preparation strategy
            
        Returns:
            Fully processed and validated DataFrame
        """
        if self.verbose:
            logger.info("Starting Berlin real estate data processing pipeline")
        
        # Step 1: Basic webscraping data processing
        df_processed = self.process_webscraping_data(df, custom_null_values)
        
        # Step 2: Berlin-specific validation
        validation_result = self.validate_berlin_data(df_processed)
        
        # Step 3: ML preparation
        if ml_strategy != "none":
            df_processed = self.prepare_for_ml(df_processed, strategy=ml_strategy, null_strategy="preserve")
        
        if self.verbose:
            validation_status = "PASSED" if validation_result['passed'] else "FAILED"
            logger.info(f"Berlin real estate processing completed - Validation: {validation_status}")
        
        return df_processed

    # =================================================================
    # METADATA & REPORTING METHODS
    # =================================================================

    def get_processing_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Comprehensive processing summary with current data state and all metadata
        
        Args:
            df: Current DataFrame state
            
        Returns:
            Complete processing summary
        """
        summary = {
            "current_data": {
                "shape": df.shape,
                "null_counts": df.isnull().astype('int64').sum().to_dict(),
                "dtypes": df.dtypes.to_dict(),
                "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024
            },
            "processing_metadata": self.metadata.get_summary(),
            "component_stats": {
                "column_standardizer": self.column_standardizer.get_history(),
                "webscraping_cleaner": self.webscraping_cleaner.get_cleaning_stats(),
                "data_validator": self.data_validator.get_validation_stats(),
                "ml_preparer": self.ml_preparer.get_preparation_stats()
            }
        }
        
        return summary

    def get_metadata(self) -> ProcessingMetadata:
        """
        Get the ProcessingMetadata instance
        
        Returns:
            ProcessingMetadata instance with all processing history
        """
        return self.metadata

    def export_metadata_to_json(self, filepath: str):
        """
        Export processing metadata to JSON file
        
        Args:
            filepath: Path for JSON export
        """
        self.metadata.save_to_json(filepath)
        if self.verbose:
            logger.info(f"Processing metadata exported to {filepath}")

    @classmethod
    def load_with_metadata(cls, metadata_filepath: str, verbose: bool = True) -> 'DataProcessor':
        """
        Load DataProcessor with saved metadata
        
        Args:
            metadata_filepath: Path to JSON metadata file
            verbose: Enable verbose logging
            
        Returns:
            DataProcessor instance with loaded metadata and fresh components
        """
        metadata = ProcessingMetadata.load_from_json(metadata_filepath)
        processor = cls(metadata=metadata, verbose=verbose)
        
        if verbose:
            logger.info(f"DataProcessor loaded with metadata from {metadata_filepath}")
        
        return processor

    # =================================================================
    # COMPONENT ACCESS METHODS (for advanced usage)
    # =================================================================

    def get_column_standardizer(self) -> ColumnStandardizer:
        """Get direct access to ColumnStandardizer component"""
        return self.column_standardizer

    def get_webscraping_cleaner(self) -> WebscrapingDataCleaner:
        """Get direct access to WebscrapingDataCleaner component"""
        return self.webscraping_cleaner

    def get_data_validator(self) -> BerlinDataValidator:
        """Get direct access to BerlinDataValidator component"""
        return self.data_validator

    def get_ml_preparer(self) -> MLDataPreparer:
        """Get direct access to MLDataPreparer component"""
        return self.ml_preparer

    def set_verbose(self, verbose: bool):
        """
        Set verbose mode for all components
        
        Args:
            verbose: Enable/disable verbose logging
        """
        self.verbose = verbose
        self.column_standardizer.verbose = verbose
        self.webscraping_cleaner.verbose = verbose
        self.data_validator.verbose = verbose
        self.ml_preparer.verbose = verbose