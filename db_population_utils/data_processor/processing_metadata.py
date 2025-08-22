# -*- coding: utf-8 -*-
"""
ProcessingMetadata - Metadaten-Management für Data Processing Pipeline
Speichert Kontext von Loading, Processing und Validation
"""

from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
import json


@dataclass
class ProcessingMetadata:
    """
    Zentrale Metadaten-Klasse für die gesamte Data Processing Pipeline
    
    Speichert Kontext von:
    - LoadReport (aus DataLoader)
    - Processing Steps (aus DataProcessor) 
    - Validation Results
    - ML Preparation Info
    """
    
    # Source Information
    file_path: str
    file_size_mb: float = 0.0
    processing_timestamp: datetime = field(default_factory=datetime.now)
    
    # Load Report Context
    load_context: Dict[str, Any] = field(default_factory=dict)
    
    # Processing History
    processing_steps: List[Dict[str, Any]] = field(default_factory=list)
    
    # Data Quality & Validation
    validation_results: Dict[str, Any] = field(default_factory=dict)
    quality_score: Optional[int] = None
    
    # ML Preparation
    ml_preparation: Dict[str, Any] = field(default_factory=dict)
    
    # Warnings and Errors
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize derived fields"""
        if not self.processing_timestamp:
            self.processing_timestamp = datetime.now()
    
    @classmethod
    def from_load_report(cls, load_report: Union[Dict, Any], file_path: str = None) -> 'ProcessingMetadata':
        """
        Factory method: Erstelle ProcessingMetadata aus LoadReport
        
        Args:
            load_report: LoadReport object oder dict
            file_path: Optional override für file path
            
        Returns:
            ProcessingMetadata instance
        """
        # Convert LoadReport to dict if needed
        if hasattr(load_report, '__dict__'):
            report_dict = load_report.__dict__.copy()
        else:
            report_dict = dict(load_report) if load_report else {}
        
        # Extract core fields
        file_path = file_path or report_dict.get('file_path', 'unknown')
        file_size_mb = report_dict.get('file_size_mb', 0.0)
        
        # Create instance
        metadata = cls(
            file_path=file_path,
            file_size_mb=file_size_mb,
            load_context=report_dict,
            quality_score=report_dict.get('quality_score'),
            warnings=list(report_dict.get('warnings') or []),
            errors=list(report_dict.get('errors') or []),
        )
        
        return metadata
    
    def add_processing_step(self, step_name: str, details: Dict[str, Any] = None):
        """
        Füge einen Processing Step zur Historie hinzu
        
        Args:
            step_name: Name des Processing Steps
            details: Zusätzliche Details des Steps
        """
        step_info = {
            'step_name': step_name,
            'timestamp': datetime.now(),
            'details': details or {}
        }
        self.processing_steps.append(step_info)
    
    def set_validation_results(self, results: Dict[str, Any]):
        """
        Setze Validation Results
        
        Args:
            results: Validation results dictionary
        """
        self.validation_results = results.copy()
        
        # Update quality score based on validation
        if not results.get('passed', True):
            issues_count = len(results.get('issues', []))
            # Reduce quality score based on issues
            if self.quality_score:
                self.quality_score = max(0, self.quality_score - (issues_count * 10))
            else:
                self.quality_score = max(0, 100 - (issues_count * 15))
    
    def set_ml_preparation(self, strategy: str, null_strategy: str, details: Dict[str, Any] = None):
        """
        Setze ML Preparation Informationen
        
        Args:
            strategy: ML preparation strategy
            null_strategy: How nulls were handled for ML
            details: Additional preparation details
        """
        self.ml_preparation = {
            'strategy': strategy,
            'null_strategy': null_strategy,
            'timestamp': datetime.now(),
            'details': details or {}
        }
    
    def add_warning(self, warning: str):
        """Füge eine Warnung hinzu"""
        if warning not in self.warnings:
            self.warnings.append(warning)
    
    def add_error(self, error: str):
        """Füge einen Fehler hinzu"""
        if error not in self.errors:
            self.errors.append(error)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Erstelle Zusammenfassung aller Metadaten
        
        Returns:
            Summary dictionary
        """
        return {
            'source_info': {
                'file_path': self.file_path,
                'file_size_mb': self.file_size_mb,
                'processing_timestamp': self.processing_timestamp.isoformat()
            },
            'data_quality': {
                'quality_score': self.quality_score,
                'validation_passed': self.validation_results.get('passed'),
                'total_warnings': len(self.warnings),
                'total_errors': len(self.errors)
            },
            'processing_info': {
                'total_steps': len(self.processing_steps),
                'last_step': self.processing_steps[-1]['step_name'] if self.processing_steps else None,
                'ml_prepared': bool(self.ml_preparation)
            },
            'load_info': {
                'detected_format': self.load_context.get('detected_format'),
                'total_rows': self.load_context.get('total_rows', 0),
                'total_columns': self.load_context.get('total_columns', 0),
                'loading_time_seconds': self.load_context.get('loading_time_seconds', 0)
            }
        }
    
    def export_to_dict(self) -> Dict[str, Any]:
        """
        Export zu Dictionary (für JSON serialization)
        
        Returns:
            Dictionary representation
        """
        return {
            'file_path': self.file_path,
            'file_size_mb': self.file_size_mb,
            'processing_timestamp': self.processing_timestamp.isoformat(),
            'load_context': self.load_context,
            'processing_steps': [
                {
                    **step,
                    'timestamp': step['timestamp'].isoformat() if isinstance(step['timestamp'], datetime) else step['timestamp']
                } 
                for step in self.processing_steps
            ],
            'validation_results': self.validation_results,
            'quality_score': self.quality_score,
            'ml_preparation': {
                **self.ml_preparation,
                'timestamp': self.ml_preparation['timestamp'].isoformat() 
                if 'timestamp' in self.ml_preparation and isinstance(self.ml_preparation['timestamp'], datetime)
                else self.ml_preparation.get('timestamp')
            } if self.ml_preparation else {},
            'warnings': self.warnings,
            'errors': self.errors
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessingMetadata':
        """
        Lade ProcessingMetadata aus Dictionary
        
        Args:
            data: Dictionary representation
            
        Returns:
            ProcessingMetadata instance
        """
        # Parse timestamps
        processing_timestamp = datetime.fromisoformat(data['processing_timestamp']) if data.get('processing_timestamp') else datetime.now()
        
        processing_steps = []
        for step in data.get('processing_steps', []):
            step_copy = step.copy()
            if 'timestamp' in step_copy:
                step_copy['timestamp'] = datetime.fromisoformat(step_copy['timestamp']) if isinstance(step_copy['timestamp'], str) else step_copy['timestamp']
            processing_steps.append(step_copy)
        
        ml_preparation = data.get('ml_preparation', {}).copy()
        if 'timestamp' in ml_preparation and isinstance(ml_preparation['timestamp'], str):
            ml_preparation['timestamp'] = datetime.fromisoformat(ml_preparation['timestamp'])
        
        return cls(
            file_path=data['file_path'],
            file_size_mb=data.get('file_size_mb', 0.0),
            processing_timestamp=processing_timestamp,
            load_context=data.get('load_context', {}),
            processing_steps=processing_steps,
            validation_results=data.get('validation_results', {}),
            quality_score=data.get('quality_score'),
            ml_preparation=ml_preparation,
            warnings=data.get('warnings', []),
            errors=data.get('errors', [])
        )
    
    def save_to_json(self, filepath: str):
        """
        Speichere Metadaten als JSON File
        
        Args:
            filepath: Path to save JSON file
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.export_to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_json(cls, filepath: str) -> 'ProcessingMetadata':
        """
        Lade Metadaten aus JSON File
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            ProcessingMetadata instance
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)