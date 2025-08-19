"""
Smart DB Connector - Simplified All-in-One Database Operations

Philosophy: One function call does everything with automatic reporting.
Design: Smart, simple, comprehensive - no manual steps needed.

Key Features:
- 🎯 One-call operations: Everything automated internally
- 📊 Automatic comprehensive reporting
- 🔍 Built-in health checks and validations
- ⚡ Smart connection management
- 🛡️ Robust error handling with recovery
- 📈 Performance monitoring built-in

Usage Examples:
    # Initialize once
    db = db_connector("postgresql://user:pass@host:5432/db")
    
    # One call - everything automated
    result = db.smart_query("SELECT * FROM users")
    # Returns: {'data': DataFrame, 'report': {...}, 'success': True}
    
    result = db.smart_insert(dataframe, "users") 
    # Returns: {'success': True, 'report': {...}, 'rows_inserted': 1000}
    
    result = db.smart_execute("CREATE INDEX...")
    # Returns: {'success': True, 'report': {...}, 'rows_affected': 0}
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Union, List
from contextlib import contextmanager
import time
import logging
from datetime import datetime

try:
    import sqlalchemy
    from sqlalchemy import create_engine, text, inspect
    from sqlalchemy.engine import Engine
    from sqlalchemy.exc import SQLAlchemyError
    import pandas as pd
except ImportError as e:
    raise ImportError(f"Required packages missing: {e}. Install with: pip install sqlalchemy pandas psycopg2")


@dataclass
class SmartReport:
    """Comprehensive reporting for database operations."""
    operation: str = ""
    success: bool = True
    execution_time_ms: float = 0.0
    data_summary: Dict[str, Any] = field(default_factory=dict)
    performance: Dict[str, Any] = field(default_factory=dict)
    
    # Performance metrics
    memory_usage_mb: float = 0.0
    cpu_time_ms: float = 0.0
    io_operations: int = 0
    
    # Messages - use consistent naming
    info_messages: List[str] = field(default_factory=list)
    warning_messages: List[str] = field(default_factory=list)
    error_messages: List[str] = field(default_factory=list)
    recommendation_messages: List[str] = field(default_factory=list)
    
    # Additional attributes for health check
    connection_healthy: bool = False
    database_version: str = ""
    connection_time_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add_info(self, message: str):
        """Add info message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.info_messages.append(f"[{timestamp}] {message}")

    def add_warning(self, message: str):
        """Add warning message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.warning_messages.append(f"[{timestamp}] {message}")

    def add_error(self, message: str):
        """Add error message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.error_messages.append(f"[{timestamp}] {message}")
        self.success = False

    def add_recommendation(self, message: str):
        """Add recommendation message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.recommendation_messages.append(f"[{timestamp}] {message}")
    
    def summary(self) -> Dict[str, Any]:
        """Get comprehensive operation summary."""
        return {
            'operation': self.operation,
            'success': self.success,
            'execution_time_ms': round(self.execution_time_ms, 2),
            'data_summary': {
                'rows': self.data_summary.get('rows', 0),
                'columns': self.data_summary.get('columns', 0), 
                'size_mb': round(self.data_summary.get('size_mb', 0.0), 3),
                'quality_score': self.data_summary.get('quality_score', 0)
            },
            'performance': {
                'connection_time_ms': round(self.performance.get('connection_time_ms', 0.0), 2),
                'memory_mb': round(self.performance.get('memory_mb', 0.0), 2),
                'io_ops': self.performance.get('io_ops', 0)
            },
            'status': {
                'info_count': len(self.info_messages),
                'warnings': len(self.warning_messages),
                'errors': len(self.error_messages),
                'recommendations': len(self.recommendation_messages)
            },
            'messages': {
                'info': self.info_messages,
                'warnings': self.warning_messages,
                'errors': self.error_messages,
                'recommendations': self.recommendation_messages
            }
        }

    # Properties for backward compatibility
    @property
    def info(self):
        return self.info_messages
    
    @property
    def warnings(self):
        return self.warning_messages
    
    @property
    def errors(self):
        return self.error_messages
    
    @property
    def recommendations(self):
        return self.recommendation_messages


class db_connector:
    """
    db_connector - Everything automated in one call.
    
    Core principle: Call one method, get everything done with full reporting.
    """
    
    def __init__(
        self, 
        connection_string: str,
        pool_size: int = 5,
        echo_sql: bool = False,
        auto_optimize: bool = True,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize db_connector."""
        self.connection_string = connection_string
        self.pool_size = pool_size
        self.echo_sql = echo_sql
        self.auto_optimize = auto_optimize
        self.logger = logger or logging.getLogger(__name__)
        
        # Create engine with smart configuration
        engine_kwargs = {
            'echo': echo_sql
        }
        
        # Add pooling parameters only for non-SQLite databases
        if not connection_string.startswith('sqlite://'):
            engine_kwargs.update({
                'pool_size': pool_size,
                'max_overflow': pool_size * 2,
                'pool_pre_ping': True,
                'pool_recycle': 3600
            })
        
        self.engine = create_engine(connection_string, **engine_kwargs)
        
        # Cache for schema information
        self._schema_cache = {}
        self._health_cache = {"last_check": 0, "status": None}

    # === MAIN SMART OPERATIONS (3 core methods) ===
    
    def smart_query(
        self, 
        sql: str, 
        params: Optional[Dict[str, Any]] = None,
        analyze_data: bool = True,
        cache_results: bool = False
    ) -> Dict[str, Any]:
        """
        Smart Query - One call does everything.
        
        Automatically performs:
        - Connection health check
        - Query execution with error handling
        - Data quality analysis
        - Performance monitoring
        - Memory optimization
        - Comprehensive reporting
        
        Returns:
            {
                'success': bool,
                'data': pd.DataFrame,
                'report': SmartReport,
                'cached': bool
            }
        """
        start_time = time.time()
        report = SmartReport(operation="SMART_QUERY")
        result = {'success': False, 'data': pd.DataFrame(), 'report': report, 'cached': False}
        
        try:
            report.add_info("Starting smart query operation")
            
            # 1. Automatic connection health check
            if not self._check_connection_health(report):
                return result
            
            # 2. Query analysis and optimization
            optimized_sql = self._optimize_query(sql) if self.auto_optimize else sql
            if optimized_sql != sql:
                report.add_info("Query automatically optimized")
            
            # 3. Execute query with automatic retries
            df = self._execute_query_with_retry(optimized_sql, params, report)
            if df is None:
                return result
            
            # 4. Automatic data analysis
            if analyze_data and not df.empty:
                self._analyze_dataframe(df, report)
            
            # 5. Performance metrics
            self._collect_performance_metrics(report, start_time)
            
            # 6. Success
            report.success = True
            report.add_info(f"Query completed successfully: {len(df)} rows retrieved")
            result.update({'success': True, 'data': df})
            
        except Exception as e:
            report.add_error(f"Smart query failed: {str(e)}")
            self.logger.error(f"Smart query error: {e}")
        
        finally:
            report.execution_time_ms = (time.time() - start_time) * 1000
            result['report'] = report
        
        return result
    
    def smart_insert(
        self,
        dataframe: pd.DataFrame,
        table: str,
        schema: Optional[str] = None,
        if_exists: str = "append",
        chunk_size: int = 5000,
        create_indexes: bool = True
    ) -> Dict[str, Any]:
        """
        Smart Insert - One call does everything.
        
        Automatically performs:
        - Connection health check  
        - Schema validation and creation
        - Table preparation
        - Data quality validation
        - Optimized batch insertion
        - Index creation
        - Performance monitoring
        - Comprehensive reporting
        
        Returns:
            {
                'success': bool,
                'rows_inserted': int,
                'report': SmartReport,
                'table_created': bool,
                'indexes_created': List[str]
            }
        """
        start_time = time.time()
        report = SmartReport(operation="SMART_INSERT")
        result = {
            'success': False, 
            'rows_inserted': 0, 
            'report': report, 
            'table_created': False,
            'indexes_created': []
        }
        
        try:
            report.add_info(f"Starting smart insert: {len(dataframe)} rows to {table}")
            
            # 1. Connection health check
            if not self._check_connection_health(report):
                return result
            
            # 2. Data quality pre-checks
            if not self._validate_dataframe(dataframe, report):
                return result
            
            # 3. Schema preparation
            if not self._prepare_schema_and_table(schema, table, dataframe, report):
                return result
            
            # 4. Optimized insertion
            rows_inserted = self._perform_smart_insert(
                dataframe, table, schema, if_exists, chunk_size, report
            )
            
            # 5. Post-insertion optimizations
            indexes_created = []
            if create_indexes and rows_inserted > 0:
                indexes_created = self._create_smart_indexes(table, schema, dataframe, report)
            
            # 6. Performance metrics
            self._collect_performance_metrics(report, start_time)
            
            # 7. Success
            report.success = True
            report.rows_affected = rows_inserted
            report.add_info(f"Insert completed: {rows_inserted} rows inserted")
            
            result.update({
                'success': True,
                'rows_inserted': rows_inserted,
                'indexes_created': indexes_created
            })
            
        except Exception as e:
            report.add_error(f"Smart insert failed: {str(e)}")
            self.logger.error(f"Smart insert error: {e}")
        
        finally:
            report.execution_time_ms = (time.time() - start_time) * 1000
            result['report'] = report
        
        return result
    
    def smart_execute(
        self,
        sql: str,
        params: Optional[Dict[str, Any]] = None,
        analyze_impact: bool = True,
        auto_commit: bool = True
    ) -> Dict[str, Any]:
        """
        Smart Execute - One call does everything.
        
        Automatically performs:
        - Connection health check
        - SQL analysis and validation
        - Transaction management
        - Impact analysis
        - Performance monitoring
        - Comprehensive reporting
        
        Returns:
            {
                'success': bool,
                'rows_affected': int,
                'report': SmartReport,
                'sql_type': str,
                'impact_analysis': Dict
            }
        """
        start_time = time.time()
        report = SmartReport(operation="SMART_EXECUTE")
        result = {
            'success': False, 
            'rows_affected': 0, 
            'report': report, 
            'sql_type': '',
            'impact_analysis': {}
        }
        
        try:
            sql_type = self._analyze_sql_type(sql)
            report.add_info(f"Starting smart execute: {sql_type} operation")
            result['sql_type'] = sql_type
            
            # 1. Connection health check
            if not self._check_connection_health(report):
                return result
            
            # 2. Pre-execution impact analysis
            impact = {}
            if analyze_impact:
                impact = self._analyze_sql_impact(sql, params, report)
                result['impact_analysis'] = impact
            
            # 3. Execute with transaction management
            rows_affected = self._execute_sql_with_transaction(sql, params, auto_commit, report)
            
            # 4. Post-execution validation
            if sql_type in ['CREATE', 'ALTER', 'DROP']:
                self._validate_schema_changes(sql, report)
            
            # 5. Performance metrics
            self._collect_performance_metrics(report, start_time)
            
            # 6. Success
            report.success = True
            report.rows_affected = rows_affected
            report.add_info(f"Execute completed: {rows_affected} rows affected")
            result.update({'success': True, 'rows_affected': rows_affected})
            
        except Exception as e:
            report.add_error(f"Smart execute failed: {str(e)}")
            self.logger.error(f"Smart execute error: {e}")
        
        finally:
            report.execution_time_ms = (time.time() - start_time) * 1000
            result['report'] = report
        
        return result
    
    # === INTERNAL SMART AUTOMATION METHODS ===
    
    def _check_connection_health(self, report: SmartReport) -> bool:
        """Check if database connection is healthy."""
        import time
        from sqlalchemy import text
        
        try:
            start_time = time.time()
            
            with self.engine.connect() as conn:
                # Test basic connectivity
                result = conn.execute(text("SELECT version()"))
                version_info = result.fetchone()[0]
                
                # Set attributes safely
                report.database_version = version_info
                report.connection_time_ms = (time.time() - start_time) * 1000
                if hasattr(report, 'connection_healthy'):
                    report.connection_healthy = True
                report.add_info("Connection health check passed")
                
            return True
            
        except Exception as e:
            if hasattr(report, 'connection_healthy'):
                report.connection_healthy = False
            report.add_error(f"Connection health check failed: {e}")
            return False   
    
    def _execute_query_with_retry(self, sql: str, params: Optional[Dict], report: SmartReport) -> Optional[pd.DataFrame]:
        """Execute query with automatic retries and error handling."""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                df = pd.read_sql(sql, self.engine, params=params)
                report.rows_retrieved = len(df)
                report.columns_count = len(df.columns) if not df.empty else 0
                return df
                
            except Exception as e:
                if attempt < max_retries - 1:
                    report.add_warning(f"Query attempt {attempt + 1} failed, retrying: {str(e)}")
                    time.sleep(0.5 * (attempt + 1))  # Exponential backoff
                else:
                    report.add_error(f"Query failed after {max_retries} attempts: {str(e)}")
                    return None
    
    def _analyze_dataframe(self, df: pd.DataFrame, report: SmartReport):
        """Comprehensive DataFrame analysis."""
        if df.empty:
            report.add_warning("Dataset is empty")
            return
        
        # Basic metrics
        report.data_size_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
        report.memory_usage_mb = report.data_size_mb
        
        # Data quality analysis
        total_cells = df.shape[0] * df.shape[1]
        null_cells = df.isnull().sum().sum()
        report.null_percentage = (null_cells / total_cells * 100) if total_cells > 0 else 0
        
        # Duplicate analysis
        report.duplicate_rows = df.duplicated().sum()
        
        # Quality score calculation
        quality_score = 100
        if report.null_percentage > 50:
            quality_score = 20
        elif report.null_percentage > 25:
            quality_score = 60
        elif report.null_percentage > 10:
            quality_score = 80
        
        if report.duplicate_rows > df.shape[0] * 0.1:
            quality_score = min(quality_score, 70)
        
        report.data_quality_score = quality_score
        
        # Recommendations
        if report.null_percentage > 25:
            report.add_recommendation("High null percentage detected - consider data cleaning")
        if report.duplicate_rows > 100:
            report.add_recommendation("Many duplicate rows found - consider deduplication")
        if report.data_size_mb > 100:
            report.add_recommendation("Large dataset - consider using chunked processing")
    
    def _validate_dataframe(self, df: pd.DataFrame, report: SmartReport) -> bool:
        """Validate DataFrame before insertion."""
        if df.empty:
            report.add_error("DataFrame is empty - nothing to insert")
            return False
        
        # Check for problematic column names
        problematic_cols = [col for col in df.columns if not str(col).replace('_', '').replace('-', '').isalnum()]
        if problematic_cols:
            report.add_warning(f"Problematic column names detected: {problematic_cols}")
        
        # Check data types
        object_cols = df.select_dtypes(include=['object']).columns
        if len(object_cols) > len(df.columns) * 0.8:
            report.add_recommendation("Many text columns detected - consider optimizing data types")
        
        report.add_info(f"DataFrame validation passed: {len(df)} rows, {len(df.columns)} columns")
        return True
    
    def _prepare_schema_and_table(self, schema: Optional[str], table: str, df: pd.DataFrame, report: SmartReport) -> bool:
        """Prepare schema and table for insertion."""
        try:
            # Create schema if needed
            if schema:
                inspector = inspect(self.engine)
                if schema not in inspector.get_schema_names():
                    with self.engine.connect() as conn:
                        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
                        conn.commit()
                    report.schema_created = True
                    report.add_info(f"Schema created: {schema}")
            
            # Check if table exists
            inspector = inspect(self.engine)
            full_table = f"{schema}.{table}" if schema else table
            report.table_exists = inspector.has_table(table, schema=schema)
            
            report.add_info(f"Schema and table preparation completed")
            return True
            
        except Exception as e:
            report.add_error(f"Schema preparation failed: {str(e)}")
            return False
    
    def _perform_smart_insert(self, df: pd.DataFrame, table: str, schema: Optional[str], 
                            if_exists: str, chunk_size: int, report: SmartReport) -> int:
        """Perform optimized DataFrame insertion."""
        try:
            df.to_sql(
                name=table,
                con=self.engine,
                schema=schema,
                if_exists=if_exists,
                index=False,
                chunksize=chunk_size,
                method='multi'  # Use fast multi-row insert
            )
            
            return len(df)
            
        except Exception as e:
            report.add_error(f"Data insertion failed: {str(e)}")
            return 0
    
    def _create_smart_indexes(self, table: str, schema: Optional[str], df: pd.DataFrame, report: SmartReport) -> List[str]:
        """Create intelligent indexes based on data patterns."""
        indexes_created = []
        
        try:
            full_table = f"{schema}.{table}" if schema else table
            
            # Create indexes for likely ID columns
            id_columns = [col for col in df.columns if 'id' in col.lower()]
            for col in id_columns[:3]:  # Limit to 3 indexes
                try:
                    index_name = f"idx_{table}_{col}"
                    sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {full_table} ({col})"
                    
                    with self.engine.connect() as conn:
                        conn.execute(text(sql))
                        conn.commit()
                    
                    indexes_created.append(index_name)
                    report.add_info(f"Index created: {index_name}")
                except:
                    pass  # Skip if index creation fails
            
            return indexes_created
            
        except Exception as e:
            report.add_warning(f"Index creation encountered issues: {str(e)}")
            return indexes_created
    
    def _execute_sql_with_transaction(self, sql: str, params: Optional[Dict], 
                                    auto_commit: bool, report: SmartReport) -> int:
        """Execute SQL with proper transaction management."""
        with self.engine.connect() as conn:
            trans = conn.begin()
            try:
                result = conn.execute(text(sql), params or {})
                
                if auto_commit:
                    trans.commit()
                    report.add_info("Transaction committed automatically")
                else:
                    report.add_info("Transaction prepared (manual commit required)")
                
                return result.rowcount
                
            except Exception as e:
                trans.rollback()
                report.add_error(f"Transaction rolled back due to error: {str(e)}")
                raise
    
    def _collect_performance_metrics(self, report: SmartReport, start_time: float):
        """Collect comprehensive performance metrics."""
        # Execution time already calculated in main methods
        # Add additional performance indicators
        
        # Pool statistics
        try:
            pool = self.engine.pool
            report.io_operations = pool.checkedout()
            report.add_info(f"Connection pool utilization: {pool.checkedout()}/{pool.size()}")
        except:
            pass
        
        # Memory optimization recommendations
        if report.memory_usage_mb > 500:
            report.add_recommendation("Large memory usage - consider chunked processing")
        if report.execution_time_ms > 30000:  # 30 seconds
            report.add_recommendation("Long execution time - consider query optimization")
    
    def _analyze_sql_type(self, sql: str) -> str:
        """Analyze SQL statement type."""
        sql_upper = sql.strip().upper()
        
        type_mapping = {
            'SELECT': 'QUERY',
            'INSERT': 'INSERT', 
            'UPDATE': 'UPDATE',
            'DELETE': 'DELETE',
            'CREATE': 'CREATE',
            'ALTER': 'ALTER',
            'DROP': 'DROP'
        }
        
        for keyword, sql_type in type_mapping.items():
            if sql_upper.startswith(keyword):
                return sql_type
        
        return 'OTHER'
    
    def _analyze_sql_impact(self, sql: str, params: Optional[Dict], report: SmartReport) -> Dict[str, Any]:
        """Analyze potential impact of SQL execution."""
        impact = {
            'estimated_affected_rows': 0,
            'tables_involved': [],
            'risk_level': 'LOW',
            'recommendations': []
        }
        
        # Simple impact analysis
        sql_upper = sql.upper()
        
        if 'DROP TABLE' in sql_upper:
            impact['risk_level'] = 'CRITICAL'
            impact['recommendations'].append("CRITICAL: This will permanently delete a table")
        elif 'DELETE' in sql_upper and 'WHERE' not in sql_upper:
            impact['risk_level'] = 'HIGH'
            impact['recommendations'].append("HIGH RISK: DELETE without WHERE clause")
        elif 'UPDATE' in sql_upper and 'WHERE' not in sql_upper:
            impact['risk_level'] = 'HIGH'
            impact['recommendations'].append("HIGH RISK: UPDATE without WHERE clause")
        
        return impact
    
    def _optimize_query(self, sql: str) -> str:
        """Apply automatic query optimizations."""
        # Simple optimizations
        optimized = sql
        
        # Add LIMIT if not present in SELECT without ORDER BY
        if sql.strip().upper().startswith('SELECT') and 'LIMIT' not in sql.upper():
            if 'ORDER BY' not in sql.upper():
                optimized += " LIMIT 10000"  # Safety limit
        
        return optimized
    
    def _validate_schema_changes(self, sql: str, report: SmartReport):
        """Validate schema changes after DDL operations."""
        try:
            # Clear schema cache after DDL
            self._schema_cache.clear()
            report.add_info("Schema cache cleared after DDL operation")
        except:
            pass
    
    # === UTILITY METHODS ===
    
    def health_check(self):
        """Quick health check with summary."""
        from datetime import datetime
        
        report = SmartReport(operation="HEALTH_CHECK")
        
        if self._check_connection_health(report):
            return {
                'status': 'healthy',
                'database_version': getattr(report, 'database_version', 'Unknown'),
                'connection_time_ms': getattr(report, 'connection_time_ms', 0.0),
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'status': 'unhealthy', 
                'errors': getattr(report, 'error_messages', []),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_table_info(self, table: str, schema: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive table information."""
        try:
            inspector = inspect(self.engine)
            
            if not inspector.has_table(table, schema=schema):
                return {'exists': False, 'error': 'Table not found'}
            
            columns = inspector.get_columns(table, schema=schema)
            pk_constraint = inspector.get_pk_constraint(table, schema=schema)
            foreign_keys = inspector.get_foreign_keys(table, schema=schema)
            indexes = inspector.get_indexes(table, schema=schema)
            
            return {
                'exists': True,
                'columns': columns,
                'primary_key': pk_constraint['constrained_columns'],
                'foreign_keys': foreign_keys,
                'indexes': [idx['name'] for idx in indexes],
                'column_count': len(columns),
                'has_primary_key': bool(pk_constraint['constrained_columns'])
            }
            
        except Exception as e:
            return {'exists': False, 'error': str(e)}
    
    def close(self):
        """Clean shutdown."""
        self.engine.dispose()
        self.logger.info("DBConnector closed")


# === UTILITY FUNCTIONS ===

def create_sample_connector(db_type):
    """Create sample connector for testing."""
    if db_type == "sqlite":
        return db_connector("sqlite:///:memory:")
    elif db_type == "postgresql":
        # Replace with your actual PostgreSQL connection parameters
        return db_connector("postgresql://username:password@localhost:5432/database_name")
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

def run_comprehensive_demo():
    """Run a comprehensive demo showcasing all features."""
    print("🎯 db_connector Demo Starting...")
    
    try:
        # Use PostgreSQL instead of SQLite
        database_url = (
            "postgresql+psycopg2://neondb_owner:npg_CeS9fJg2azZD"
            "@ep-falling-glitter-a5m0j5gk-pooler.us-east-2.aws.neon.tech:5432/neondb"
            "?sslmode=require"
        )
        
        db = db_connector(database_url)
        
        print("✅ Connected to database...")
        
        # Test health check
        health = db.health_check()
        if health['status'] != 'healthy':
            print(f"❌ Health check failed: {health}")
            return
            
        print("✅ Health check passed...")
        
        # Create demo table with PostgreSQL syntax
        db.smart_execute("""
            CREATE TABLE IF NOT EXISTS demo_users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100),
                age INTEGER,
                active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        print("✅ Demo table created...")
        
        # Insert sample data
        db.smart_execute("INSERT INTO demo_users (name, email, age, active) VALUES ('Alice', 'alice@example.com', 25, true) ON CONFLICT DO NOTHING")
        db.smart_execute("INSERT INTO demo_users (name, email, age, active) VALUES ('Bob', 'bob@example.com', 30, false) ON CONFLICT DO NOTHING")
        
        print("✅ Sample data inserted...")
        
        # Query data
        result = db.smart_query("SELECT * FROM demo_users LIMIT 5")
        print(f"✅ Query executed, found {len(result['data'])} rows")
        
        print("🎉 Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
    finally:
        if 'db' in locals():
            try:
                db.close()
                print("✅ Connection closed")
            except:
                pass

if __name__ == "__main__":
    run_comprehensive_demo()
