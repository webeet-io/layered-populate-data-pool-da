# -*- coding: utf-8 -*-
"""
MLDataPreparer - Spezialisiert auf Machine Learning Daten-Vorbereitung
Einzelne Verantwortlichkeit: Daten für ML-Pipeline optimieren
"""

import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from .utils import count_true, col_null_counts

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class MLDataPreparer:
    """
    Spezialisierte Klasse für Machine Learning Datenvorbereitung
    
    Verantwortlichkeiten:
    - Null-Handling-Strategien für ML
    - Feature Engineering Empfehlungen
    - Datentyp-Optimierung für ML
    - ML-Pipeline Kompatibilität
    """
    
    def __init__(self, verbose: bool = True):
        """
        Initialize MLDataPreparer
        
        Args:
            verbose: Enable detailed logging
        """
        self.verbose = verbose
        self.preparation_history: List[Dict[str, Any]] = []
    
    def prepare_for_ml(self, 
                      df: pd.DataFrame, 
                      strategy: str = "preserve", 
                      null_strategy: str = "preserve",
                      target_column: Optional[str] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Prepare DataFrame for ML pipeline with flexible strategies
        
        Args:
            df: Input DataFrame
            strategy: ML preparation strategy ('preserve', 'minimal', 'full')
            null_strategy: How to handle nulls ('preserve', 'drop', 'mark', 'impute')
            target_column: Optional target column name for supervised learning
            
        Returns:
            Tuple[pd.DataFrame, Dict]: (prepared_df, preparation_report)
        """
        df_copy = df.copy()
        preparation_info = {
            'original_shape': df_copy.shape,
            'null_counts_before': df_copy.isnull().astype('int64').sum().to_dict(),
            'strategy': strategy,
            'null_strategy': null_strategy,
            'target_column': target_column,
            'preparation_timestamp': datetime.now()
        }
        
        # Handle nulls according to strategy
        df_copy, null_handling_info = self._handle_nulls(df_copy, null_strategy, target_column)
        preparation_info['null_handling'] = null_handling_info
        
        # Apply ML preparation strategy
        df_copy, strategy_info = self._apply_ml_strategy(df_copy, strategy, target_column)
        preparation_info['strategy_info'] = strategy_info
        
        # Final preparation info
        preparation_info['final_shape'] = df_copy.shape
        preparation_info['null_counts_after'] = df_copy.isnull().astype('int64').sum().to_dict()
        preparation_info['recommendations'] = self._generate_ml_recommendations(df_copy, target_column)
        
        # Store in history
        self.preparation_history.append(preparation_info)
        
        if self.verbose:
            logger.info(f"ML preparation completed: strategy={strategy}, null_strategy={null_strategy}")
            logger.info(f"Shape change: {preparation_info['original_shape']} → {preparation_info['final_shape']}")
        
        return df_copy, preparation_info
    
    def _handle_nulls(self, 
                     df: pd.DataFrame, 
                     null_strategy: str, 
                     target_column: Optional[str] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Handle null values according to specified strategy"""
        df_result = df.copy()
        null_info = {'strategy': null_strategy}
        
        if null_strategy == "preserve":
            # Keep NaNs for ML pipeline to handle
            null_info['action'] = 'preserved_for_ml_pipeline'
            null_info['null_columns'] = df_result.isnull().astype('int64').sum().to_dict()
            
        elif null_strategy == "drop":
            # Drop rows with any nulls
            initial_rows = len(df_result)
            df_result = df_result.dropna()
            dropped_rows = initial_rows - len(df_result)
            null_info['action'] = f'dropped_{dropped_rows}_rows_with_nulls'
            null_info['rows_dropped'] = dropped_rows
            null_info['rows_remaining'] = len(df_result)
            
        elif null_strategy == "mark":
            # Create indicator columns for missing values
            null_indicators = []
            for col in df_result.columns:
                if df_result[col].isnull().any() and col != target_column:
                    indicator_col = f"{col}_was_missing"
                    df_result[indicator_col] = df_result[col].isnull().astype(int)
                    null_indicators.append(indicator_col)
            
            null_info['action'] = f'added_{len(null_indicators)}_null_indicators'
            null_info['null_indicator_columns'] = null_indicators
            
        elif null_strategy == "impute":
            # Intelligent imputation based on data types
            imputation_summary = self._perform_imputation(df_result, target_column)
            null_info['action'] = 'imputed_missing_values'
            null_info['imputation_summary'] = imputation_summary
            
        elif null_strategy == "smart_drop":
            # Drop columns with too many nulls, then drop rows
            initial_shape = df_result.shape
            
            # Drop columns with >70% nulls (except target)
            null_ratios = df_result.isnull().astype('int64').sum() / len(df_result)
            cols_to_drop = [col for col, ratio in null_ratios.items() 
                           if ratio > 0.7 and col != target_column]
            
            if cols_to_drop:
                df_result = df_result.drop(columns=cols_to_drop)
            
            # Drop rows with nulls in remaining columns
            df_result = df_result.dropna()
            
            null_info['action'] = 'smart_drop_columns_and_rows'
            null_info['columns_dropped'] = cols_to_drop
            null_info['shape_change'] = f'{initial_shape} → {df_result.shape}'
        
        return df_result, null_info
    
    def _perform_imputation(self, df: pd.DataFrame, target_column: Optional[str] = None) -> Dict[str, Any]:
        """Perform intelligent imputation based on column types"""
        imputation_summary = {}
        
        # Separate numeric and categorical columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Remove target column from imputation if specified
        if target_column:
            numeric_cols = [col for col in numeric_cols if col != target_column]
            categorical_cols = [col for col in categorical_cols if col != target_column]
        
        # Impute numeric columns with median
        for col in numeric_cols:
            if df[col].isnull().any():
                null_count = df[col].isnull().astype('int64').sum()
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val)
                imputation_summary[col] = {
                    'type': 'numeric',
                    'method': 'median',
                    'value_used': median_val,
                    'nulls_filled': null_count
                }
        
        # Impute categorical columns with mode or 'UNKNOWN'
        for col in categorical_cols:
            if df[col].isnull().any():
                null_count = df[col].isnull().astype('int64').sum()
                mode_values = df[col].mode()
                
                if len(mode_values) > 0:
                    fill_value = mode_values[0]
                    method = 'mode'
                else:
                    fill_value = 'UNKNOWN'
                    method = 'constant'
                
                df[col] = df[col].fillna(fill_value)
                imputation_summary[col] = {
                    'type': 'categorical',
                    'method': method,
                    'value_used': fill_value,
                    'nulls_filled': null_count
                }
        
        return imputation_summary
    
    def _apply_ml_strategy(self, 
                          df: pd.DataFrame, 
                          strategy: str, 
                          target_column: Optional[str] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Apply ML preparation strategy"""
        df_result = df.copy()
        strategy_info = {'strategy': strategy}
        
        if strategy == "preserve":
            # Minimal changes - preserve original data structure
            strategy_info['actions'] = ['data_preserved']
            
        elif strategy == "minimal":
            # Basic preparation - data type optimization
            optimization_info = self._optimize_data_types(df_result)
            strategy_info['actions'] = ['data_types_optimized']
            strategy_info['optimization_info'] = optimization_info
            
        elif strategy == "full":
            # Comprehensive preparation
            actions = []
            
            # 1. Data type optimization
            optimization_info = self._optimize_data_types(df_result)
            actions.append('data_types_optimized')
            strategy_info['optimization_info'] = optimization_info
            
            # 2. Feature analysis
            feature_analysis = self._analyze_features_for_ml(df_result, target_column)
            actions.append('feature_analysis_completed')
            strategy_info['feature_analysis'] = feature_analysis
            
            # 3. Generate ML recommendations
            ml_recommendations = self._generate_detailed_ml_recommendations(df_result, target_column)
            actions.append('ml_recommendations_generated')
            strategy_info['ml_recommendations'] = ml_recommendations
            
            strategy_info['actions'] = actions
        
        return df_result, strategy_info
    
    def _optimize_data_types(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Optimize data types for better ML performance"""
        optimization_info = {
            'original_dtypes': df.dtypes.to_dict(),
            'optimizations': {}
        }
        
        for col in df.columns:
            original_dtype = df[col].dtype
            
            # Integer optimization
            if df[col].dtype in ['int64']:
                if df[col].min() >= -128 and df[col].max() <= 127:
                    df[col] = df[col].astype('int8')
                    optimization_info['optimizations'][col] = 'int64 → int8'
                elif df[col].min() >= -32768 and df[col].max() <= 32767:
                    df[col] = df[col].astype('int16')
                    optimization_info['optimizations'][col] = 'int64 → int16'
                elif df[col].min() >= -2147483648 and df[col].max() <= 2147483647:
                    df[col] = df[col].astype('int32')
                    optimization_info['optimizations'][col] = 'int64 → int32'
            
            # Float optimization
            elif df[col].dtype == 'float64':
                # Check if it can be converted to float32 without loss
                df_temp = df[col].astype('float32')
                if np.allclose(df[col].dropna(), df_temp.dropna(), equal_nan=True):
                    df[col] = df_temp
                    optimization_info['optimizations'][col] = 'float64 → float32'
            
            # String optimization to category if few unique values
            elif df[col].dtype == 'object':
                unique_ratio = df[col].nunique() / len(df[col])
                if unique_ratio < 0.1 and df[col].nunique() > 2:  # Low cardinality, but not binary
                    df[col] = df[col].astype('category')
                    optimization_info['optimizations'][col] = 'object → category'
        
        optimization_info['final_dtypes'] = df.dtypes.to_dict()
        optimization_info['memory_saved'] = self._calculate_memory_savings(
            optimization_info['original_dtypes'], 
            optimization_info['final_dtypes'], 
            len(df)
        )
        
        return optimization_info
    
    def _calculate_memory_savings(self, original_dtypes: Dict, final_dtypes: Dict, num_rows: int) -> Dict[str, Any]:
        """Calculate memory savings from dtype optimization"""
        dtype_sizes = {
            'int64': 8, 'int32': 4, 'int16': 2, 'int8': 1,
            'float64': 8, 'float32': 4,
            'object': 50,  # Rough estimate
            'category': 4   # Rough estimate
        }
        
        original_memory = sum(dtype_sizes.get(str(dtype), 8) for dtype in original_dtypes.values()) * num_rows
        final_memory = sum(dtype_sizes.get(str(dtype), 8) for dtype in final_dtypes.values()) * num_rows
        
        return {
            'original_memory_bytes': original_memory,
            'final_memory_bytes': final_memory,
            'memory_saved_bytes': original_memory - final_memory,
            'memory_saved_percentage': ((original_memory - final_memory) / original_memory) * 100 if original_memory > 0 else 0
        }
    
    def _analyze_features_for_ml(self, df: pd.DataFrame, target_column: Optional[str] = None) -> Dict[str, Any]:
        """Analyze features for ML suitability"""
        analysis = {
            'total_features': len(df.columns),
            'numeric_features': [],
            'categorical_features': [],
            'high_cardinality_features': [],
            'low_variance_features': [],
            'features_with_nulls': []
        }
        
        # Separate target column if specified
        feature_columns = [col for col in df.columns if col != target_column]
        
        for col in feature_columns:
            # Categorize by type
            if df[col].dtype in ['int8', 'int16', 'int32', 'int64', 'float32', 'float64']:
                analysis['numeric_features'].append(col)
                
                # Check for low variance
                if df[col].var() < 0.01:
                    analysis['low_variance_features'].append(col)
                    
            else:
                analysis['categorical_features'].append(col)
                
                # Check for high cardinality
                cardinality_ratio = df[col].nunique() / len(df)
                if cardinality_ratio > 0.8:  # More than 80% unique values
                    analysis['high_cardinality_features'].append(col)
            
            # Check for nulls
            if df[col].isnull().any():
                null_percentage = (df[col].isnull().astype('int64').sum() / len(df)) * 100
                analysis['features_with_nulls'].append({
                    'column': col,
                    'null_percentage': null_percentage
                })
        
        # Add target analysis if specified
        if target_column and target_column in df.columns:
            target_analysis = self._analyze_target_column(df[target_column])
            analysis['target_analysis'] = target_analysis
        
        return analysis
    
    def _analyze_target_column(self, target_series: pd.Series) -> Dict[str, Any]:
        """Analyze target column for ML task type determination"""
        analysis = {
            'column_name': target_series.name,
            'dtype': str(target_series.dtype),
            'null_count': target_series.isnull().astype('int64').sum(),
            'unique_values': target_series.nunique()
        }
        
        # Determine ML task type
        if target_series.dtype in ['int8', 'int16', 'int32', 'int64', 'float32', 'float64']:
            unique_count = target_series.nunique()
            if unique_count <= 10:
                analysis['suggested_task_type'] = 'classification'
                analysis['reason'] = f'Numeric with {unique_count} unique values (likely discrete classes)'
            else:
                analysis['suggested_task_type'] = 'regression'
                analysis['reason'] = f'Numeric with {unique_count} unique values (continuous)'
        else:
            analysis['suggested_task_type'] = 'classification'
            analysis['reason'] = 'Categorical target variable'
        
        # Add class distribution for classification
        if analysis['suggested_task_type'] == 'classification':
            class_counts = target_series.value_counts()
            analysis['class_distribution'] = class_counts.to_dict()
            analysis['is_balanced'] = (class_counts.max() / class_counts.min()) < 3 if len(class_counts) > 1 else True
        
        return analysis
    
    def _generate_ml_recommendations(self, df: pd.DataFrame, target_column: Optional[str] = None) -> List[str]:
        """Generate basic ML recommendations"""
        recommendations = []
        
        # Categorical encoding recommendations
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        if target_column in categorical_cols:
            categorical_cols.remove(target_column)
        
        if categorical_cols:
            recommendations.append(f"Consider encoding {len(categorical_cols)} categorical columns (one-hot or target encoding)")
        
        # Numeric scaling recommendations
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if target_column in numeric_cols:
            numeric_cols.remove(target_column)
        
        if numeric_cols:
            recommendations.append(f"Consider scaling {len(numeric_cols)} numeric columns (StandardScaler or RobustScaler)")
        
        # Null handling recommendations
        null_cols = df.isnull().astype('int64').sum()
        null_cols = null_cols[null_cols > 0]
        
        if len(null_cols) > 0:
            recommendations.append(f"Handle missing values in {len(null_cols)} columns before ML training")
        
        return recommendations
    
    def _generate_detailed_ml_recommendations(self, df: pd.DataFrame, target_column: Optional[str] = None) -> Dict[str, Any]:
        """Generate detailed ML recommendations with specific actions"""
        recommendations = {
            'preprocessing_steps': [],
            'feature_engineering': [],
            'model_suggestions': [],
            'validation_strategy': []
        }
        
        # Preprocessing recommendations
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if target_column:
            categorical_cols = [col for col in categorical_cols if col != target_column]
            numeric_cols = [col for col in numeric_cols if col != target_column]
        
        if categorical_cols:
            high_card_cols = [col for col in categorical_cols if df[col].nunique() > 20]
            low_card_cols = [col for col in categorical_cols if df[col].nunique() <= 20]
            
            if low_card_cols:
                recommendations['preprocessing_steps'].append({
                    'step': 'one_hot_encoding',
                    'columns': low_card_cols,
                    'reason': 'Low cardinality categorical columns suitable for one-hot encoding'
                })
            
            if high_card_cols:
                recommendations['preprocessing_steps'].append({
                    'step': 'target_encoding',
                    'columns': high_card_cols,
                    'reason': 'High cardinality categorical columns need target encoding or embedding'
                })
        
        if numeric_cols:
            recommendations['preprocessing_steps'].append({
                'step': 'feature_scaling',
                'columns': numeric_cols,
                'methods': ['StandardScaler', 'RobustScaler', 'MinMaxScaler'],
                'reason': 'Numeric features benefit from scaling for most ML algorithms'
            })
        
        # Feature engineering recommendations
        date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        if date_cols:
            recommendations['feature_engineering'].append({
                'technique': 'datetime_features',
                'columns': date_cols,
                'suggestions': ['extract year/month/day', 'create time-based features', 'calculate time differences']
            })
        
        coord_cols = [col for col in df.columns if any(x in col.lower() for x in ['lat', 'lng', 'lon'])]
        if len(coord_cols) >= 2:
            recommendations['feature_engineering'].append({
                'technique': 'geospatial_features',
                'columns': coord_cols,
                'suggestions': ['calculate distances', 'create location clusters', 'add geographic features']
            })
        
        # Model suggestions based on data characteristics
        data_size = len(df)
        feature_count = len([col for col in df.columns if col != target_column])
        
        if target_column and target_column in df.columns:
            target_analysis = self._analyze_target_column(df[target_column])
            
            if target_analysis['suggested_task_type'] == 'classification':
                if data_size < 1000:
                    recommendations['model_suggestions'].extend(['RandomForest', 'SVM', 'LogisticRegression'])
                elif data_size < 10000:
                    recommendations['model_suggestions'].extend(['XGBoost', 'LightGBM', 'RandomForest'])
                else:
                    recommendations['model_suggestions'].extend(['XGBoost', 'LightGBM', 'Neural Networks'])
            else:  # regression
                if data_size < 1000:
                    recommendations['model_suggestions'].extend(['RandomForest', 'SVR', 'LinearRegression'])
                elif data_size < 10000:
                    recommendations['model_suggestions'].extend(['XGBoost', 'LightGBM', 'RandomForest'])
                else:
                    recommendations['model_suggestions'].extend(['XGBoost', 'LightGBM', 'Neural Networks'])
        
        # Validation strategy recommendations
        if data_size < 1000:
            recommendations['validation_strategy'].append('Use Leave-One-Out or 10-fold cross-validation due to small dataset')
        elif data_size < 10000:
            recommendations['validation_strategy'].append('Use 5-fold or 10-fold cross-validation')
        else:
            recommendations['validation_strategy'].append('Use train/validation/test split (70/15/15) with cross-validation')
        
        return recommendations
    
    def assess_ml_readiness(self, df: pd.DataFrame, target_column: Optional[str] = None) -> Dict[str, Any]:
        """
        Assess how ready the data is for ML pipeline
        
        Args:
            df: DataFrame to assess
            target_column: Optional target column
            
        Returns:
            ML readiness assessment
        """
        assessment = {
            'overall_score': 0,
            'readiness_level': 'not_ready',
            'blocking_issues': [],
            'recommendations': [],
            'detailed_scores': {}
        }
        
        # 1. Data Quality Score (25 points)
        total_nulls = int(df.isnull().to_numpy(dtype="int64").sum())
        null_percentage = (total_nulls / (len(df) * len(df.columns))) * 100
        if null_percentage == 0:
            data_quality_score = 25
        elif null_percentage < 5:
            data_quality_score = 20
        elif null_percentage < 15:
            data_quality_score = 15
        elif null_percentage < 30:
            data_quality_score = 10
        else:
            data_quality_score = 0
            assessment['blocking_issues'].append(f'High null percentage: {null_percentage:.1f}%')
        
        assessment['detailed_scores']['data_quality'] = data_quality_score
        
        # 2. Data Size Score (25 points)
        data_size = len(df)
        if data_size >= 10000:
            data_size_score = 25
        elif data_size >= 1000:
            data_size_score = 20
        elif data_size >= 100:
            data_size_score = 15
        else:
            data_size_score = 5
            assessment['blocking_issues'].append(f'Very small dataset: {data_size} rows')
        
        assessment['detailed_scores']['data_size'] = data_size_score
        
        # 3. Feature Quality Score (25 points)
        numeric_features = len(df.select_dtypes(include=[np.number]).columns)
        categorical_features = len(df.select_dtypes(include=['object', 'category']).columns)
        total_features = numeric_features + categorical_features
        
        if target_column:
            total_features -= 1
        
        if total_features >= 5:
            feature_score = 25
        elif total_features >= 3:
            feature_score = 20
        elif total_features >= 1:
            feature_score = 10
        else:
            feature_score = 0
            assessment['blocking_issues'].append('No usable features found')
        
        # Penalize high cardinality categorical features
        high_cardinality_penalty = 0
        for col in df.select_dtypes(include=['object']).columns:
            if col != target_column:
                cardinality_ratio = df[col].nunique() / len(df)
                if cardinality_ratio > 0.8:
                    high_cardinality_penalty += 5
        
        feature_score = max(0, feature_score - high_cardinality_penalty)
        assessment['detailed_scores']['feature_quality'] = feature_score
        
        # 4. Target Column Score (25 points) - only if target specified
        if target_column:
            if target_column in df.columns:
                target_nulls = df[target_column].isnull().astype('int64').sum()
                if target_nulls == 0:
                    target_score = 25
                elif target_nulls < len(df) * 0.05:
                    target_score = 20
                elif target_nulls < len(df) * 0.15:
                    target_score = 15
                else:
                    target_score = 0
                    assessment['blocking_issues'].append(f'Target column has {target_nulls} null values')
            else:
                target_score = 0
                assessment['blocking_issues'].append(f'Target column "{target_column}" not found')
        else:
            target_score = 25  # Full score if no target specified (unsupervised learning)
        
        assessment['detailed_scores']['target_quality'] = target_score
        
        # Calculate overall score
        assessment['overall_score'] = data_quality_score + data_size_score + feature_score + target_score
        
        # Determine readiness level
        if assessment['overall_score'] >= 80:
            assessment['readiness_level'] = 'ready'
        elif assessment['overall_score'] >= 60:
            assessment['readiness_level'] = 'mostly_ready'
        elif assessment['overall_score'] >= 40:
            assessment['readiness_level'] = 'needs_work'
        else:
            assessment['readiness_level'] = 'not_ready'
        
        # Generate recommendations based on scores
        if data_quality_score < 20:
            assessment['recommendations'].append('Clean missing values and outliers')
        if data_size_score < 20:
            assessment['recommendations'].append('Consider collecting more data or using data augmentation')
        if feature_score < 20:
            assessment['recommendations'].append('Perform feature engineering or collect additional features')
        if target_score < 20 and target_column:
            assessment['recommendations'].append('Address issues with target column')
        
        return assessment
    
    def get_preparation_history(self) -> List[Dict[str, Any]]:
        """Get preparation history"""
        return self.preparation_history.copy()
    
    def get_preparation_stats(self) -> Dict[str, Any]:
        """Get summary statistics from all ML preparations"""
        if not self.preparation_history:
            return {'total_preparations': 0}
        
        strategies_used = [prep['strategy'] for prep in self.preparation_history]
        null_strategies_used = [prep['null_strategy'] for prep in self.preparation_history]
        
        return {
            'total_preparations': len(self.preparation_history),
            'strategies_used': {strategy: strategies_used.count(strategy) for strategy in set(strategies_used)},
            'null_strategies_used': {strategy: null_strategies_used.count(strategy) for strategy in set(null_strategies_used)},
            'avg_shape_reduction': self._calculate_avg_shape_reduction(),
            'most_common_recommendations': self._get_most_common_recommendations()
        }
    
    def _calculate_avg_shape_reduction(self) -> Dict[str, float]:
        """Calculate average shape reduction across all preparations"""
        if not self.preparation_history:
            return {'rows': 0, 'columns': 0}
        
        total_row_reduction = 0
        total_col_reduction = 0
        
        for prep in self.preparation_history:
            original_shape = prep['original_shape']
            final_shape = prep['final_shape']
            
            row_reduction = (original_shape[0] - final_shape[0]) / original_shape[0] * 100 if original_shape[0] > 0 else 0
            col_reduction = (original_shape[1] - final_shape[1]) / original_shape[1] * 100 if original_shape[1] > 0 else 0
            
            total_row_reduction += row_reduction
            total_col_reduction += col_reduction
        
        return {
            'avg_rows_reduction_percent': total_row_reduction / len(self.preparation_history),
            'avg_columns_reduction_percent': total_col_reduction / len(self.preparation_history)
        }
    
    def _get_most_common_recommendations(self) -> List[str]:
        """Get most common recommendations across all preparations"""
        all_recommendations = []
        
        for prep in self.preparation_history:
            recommendations = prep.get('recommendations', [])
            all_recommendations.extend(recommendations)
        
        # Count frequency
        rec_counts = {}
        for rec in all_recommendations:
            rec_counts[rec] = rec_counts.get(rec, 0) + 1
        
        # Sort by frequency and return top 5
        sorted_recs = sorted(rec_counts.items(), key=lambda x: x[1], reverse=True)
        return [rec for rec, count in sorted_recs[:5]]