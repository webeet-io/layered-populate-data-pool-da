"""
Smart Database Connector V3 - Production-Ready Version

Enhanced database connector with intelligent switching between NeonDB and AWS LayeredDB.
Optimized for production use with improved performance, error handling, and type safety.

Features:
- Intelligent database selection (NeonDB default, AWS LayeredDB when credentials provided)
- Comprehensive error handling and recovery
- Type-safe operations with full type annotations
- Performance optimizations and connection management
- Auto-discovery of schemas and tables
- Production-ready reliability and monitoring
"""

import pandas as pd
from sqlalchemy import create_engine, text, Engine
import time
import socket
import getpass
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ConnectionType(Enum):
    """Enumeration of supported database connection types"""
    NEON_DB = "NeonDB"
    AWS_LAYERED_DB = "AWS LayeredDB"


class DatabaseConnectionError(Exception):
    """Custom exception for database connection issues"""
    pass


class SchemaError(Exception):
    """Custom exception for schema-related operations"""
    pass


@dataclass
class TableInfo:
    """Data class representing table information"""
    name: str
    columns: int


@dataclass
class SchemaInfo:
    """Data class representing schema information"""
    tables: List[TableInfo]
    table_count: int


@dataclass
class TunnelStatus:
    """Data class representing tunnel connection status"""
    active: bool
    host: str
    port: int
    status: str
    message: str


class SmartReport:
    """Enhanced report class for database operations with performance tracking"""
    
    def __init__(self, operation: str) -> None:
        self.operation = operation
        self.start_time = time.time()
        self.info: List[str] = []
        self.warnings: List[str] = []
        self.errors: List[str] = []
        self.recommendations: List[str] = []
        self.execution_time = 0.0
        
    def add_info(self, message: str) -> None:
        """Add informational message to report"""
        self.info.append(message)
        
    def add_warning(self, message: str) -> None:
        """Add warning message to report"""
        self.warnings.append(message)
        
    def add_error(self, message: str) -> None:
        """Add error message to report"""
        self.errors.append(message)
        
    def add_recommendation(self, message: str) -> None:
        """Add recommendation message to report"""
        self.recommendations.append(message)
        
    def complete(self) -> None:
        """Mark operation as complete and calculate execution time"""
        self.execution_time = time.time() - self.start_time
        
    def summary(self) -> Dict[str, Any]:
        """Get comprehensive operation summary"""
        self.complete()
        return {
            'operation': self.operation,
            'execution_time_seconds': round(self.execution_time, 3),
            'info_count': len(self.info),
            'warnings_count': len(self.warnings),
            'errors_count': len(self.errors),
            'recommendations_count': len(self.recommendations),
            'status': 'completed' if len(self.errors) == 0 else 'completed_with_errors'
        }


class DatabaseConfig:
    """Centralized database configuration management with security best practices"""
    
    def __init__(self) -> None:
        self.NEON_CONFIG = {
            "connection_string": (
                "postgresql+psycopg2://neondb_owner:npg_CeS9fJg2azZD"
                "@ep-falling-glitter-a5m0j5gk-pooler.us-east-2.aws.neon.tech:5432/neondb"
                "?sslmode=require"
            ),
            "default_schema": "test_berlin_data",
            "description": "NeonDB - Primary development database"
        }
        
        self.AWS_LAYERED_CONFIG = {
            "host": "localhost",
            "port": 5433,
            "database": "layereddb", 
            "description": "AWS LayeredDB - Through SSH tunnel on localhost:5433"
        }
    
    def build_aws_connection_string(self, username: str, password: str) -> str:
        """Build AWS connection string with provided credentials"""
        if not username or not password:
            raise ValueError("Username and password are required for AWS connection")
        
        return (
            f"postgresql+psycopg2://{username}:{password}@"
            f"{self.AWS_LAYERED_CONFIG['host']}:{self.AWS_LAYERED_CONFIG['port']}/"
            f"{self.AWS_LAYERED_CONFIG['database']}"
        )
    
    def get_neon_connection_string(self) -> str:
        """Get NeonDB connection string"""
        return self.NEON_CONFIG["connection_string"]


class TunnelManager:
    """Manages SSH tunnel connection for AWS database with enhanced reliability"""
    
    def __init__(self, host: str = "localhost", port: int = 5433) -> None:
        self.host = host
        self.port = port
        
    def is_tunnel_active(self) -> bool:
        """Check if tunnel is active by testing port connectivity with timeout"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(2)
                result = sock.connect_ex((self.host, self.port))
                return result == 0
        except (socket.error, OSError):
            return False
    
    def get_tunnel_status(self) -> TunnelStatus:
        """Get detailed tunnel status information"""
        is_active = self.is_tunnel_active()
        status = 'Connected' if is_active else 'Not Connected'
        message = f"Tunnel {'is' if is_active else 'is not'} active on {self.host}:{self.port}"
        
        return TunnelStatus(
            active=is_active,
            host=self.host,
            port=self.port,
            status=status,
            message=message
        )


class SmartDbConnectorV3:
    """
    Smart Database Connector V3 - Production-Ready Database Interface
    
    Intelligent switching between NeonDB and AWS LayeredDB with:
    - Enhanced error handling and recovery mechanisms
    - Type-safe operations with comprehensive annotations
    - Performance optimizations and connection management
    - Production-ready reliability and monitoring capabilities
    """
    
    def __init__(
        self, 
        database: Optional[str] = None, 
        username: Optional[str] = None, 
        password: Optional[str] = None, 
        auto_discover: bool = True
    ) -> None:
        """
        Initialize Smart Database Connector V3
        
        Args:
            database: Target database ('layereddb' for AWS, None for NeonDB)
            username: Database username (required for AWS connection)
            password: Database password (required for AWS connection)
            auto_discover: Automatically discover schemas and tables
            
        Raises:
            DatabaseConnectionError: If connection establishment fails
        """
        
        print("🌟 SMART DATABASE CONNECTOR V3 - INITIALIZING...")
        print("=" * 60)
        
        # Initialize core properties with type safety
        self.connection_string: Optional[str] = None
        self.engine: Optional[Engine] = None
        self.available_schemas: Dict[str, SchemaInfo] = {}
        self.current_schema: Optional[str] = None
        self.connection_type: Optional[ConnectionType] = None
        self.config = DatabaseConfig()
        self.tunnel_manager: Optional[TunnelManager] = None
        
        # Determine connection type and establish connection
        self._setup_connection(database, username, password)
        
        # Perform auto-discovery if requested and connection successful
        if auto_discover and self.engine:
            self._discover_schemas()
            self._set_default_schema()
            self._show_connection_summary()
    
    def _setup_connection(
        self, 
        database: Optional[str], 
        username: Optional[str], 
        password: Optional[str]
    ) -> None:
        """Setup and establish database connection"""
        try:
            if self._should_use_aws_connection(database, username, password):
                print("🚇 AWS LayeredDB connection requested")
                self._setup_aws_connection(database, username, password)
            else:
                print("🔗 Using default NeonDB connection")
                self._setup_neon_connection()
            
            # Establish connection
            if self.connection_string:
                self._connect()
            else:
                raise DatabaseConnectionError("No valid connection string generated")
                
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to setup database connection: {e}")
    
    def _should_use_aws_connection(
        self, 
        database: Optional[str], 
        username: Optional[str], 
        password: Optional[str]
    ) -> bool:
        """Determine if AWS connection should be used"""
        return (
            database == 'layereddb' or 
            (database and username and password) or
            (username and password)
        )
    
    def _setup_neon_connection(self) -> None:
        """Setup NeonDB connection (default)"""
        self.connection_string = self.config.get_neon_connection_string()
        self.connection_type = ConnectionType.NEON_DB
        print(f"✅ NeonDB configuration loaded")
        print(f"   Default schema: {self.config.NEON_CONFIG['default_schema']}")
    
    def _setup_aws_connection(
        self, 
        database: Optional[str], 
        username: Optional[str], 
        password: Optional[str]
    ) -> None:
        """Setup AWS LayeredDB connection with enhanced credential handling"""
        
        # Get credentials interactively if not provided
        if not username or not password:
            print("\n🔐 AWS LayeredDB CONNECTION SETUP")
            print("-" * 40)
            print("Please provide your AWS database credentials:")
            
            if not username:
                username = input("Database Username: ").strip()
                if not username:
                    print("❌ Username is required for AWS connection")
                    print("🔄 Falling back to NeonDB...")
                    self._setup_neon_connection()
                    return
                    
            if not password:
                password = getpass.getpass("Database Password: ")
                if not password:
                    print("❌ Password is required for AWS connection")
                    print("🔄 Falling back to NeonDB...")
                    self._setup_neon_connection()
                    return
        
        # Check tunnel connectivity
        self.tunnel_manager = TunnelManager()
        tunnel_status = self.tunnel_manager.get_tunnel_status()
        
        print(f"🚇 Tunnel Status: {tunnel_status.status}")
        if not tunnel_status.active:
            print("⚠️  SSH tunnel not detected on localhost:5433")
            print("💡 Make sure to run your SSH tunnel script first:")
            print("   ./connect-db.sh")
            print("🔄 Falling back to NeonDB...")
            self._setup_neon_connection()
            return
        
        # Build AWS connection string with validation
        try:
            self.connection_string = self.config.build_aws_connection_string(username, password)
            self.connection_type = ConnectionType.AWS_LAYERED_DB
            print(f"✅ AWS LayeredDB configuration loaded")
            print(f"   Tunnel: {tunnel_status.message}")
        except ValueError as e:
            print(f"❌ Configuration error: {e}")
            print("🔄 Falling back to NeonDB...")
            self._setup_neon_connection()
    
    def _connect(self) -> None:
        """Establish database connection with enhanced error handling"""
        if not self.connection_string or not self.connection_type:
            raise DatabaseConnectionError("Connection not properly configured")
        
        try:
            print(f"🔌 Connecting to {self.connection_type.value}...")
            
            # Create engine with production-ready settings
            self.engine = create_engine(
                self.connection_string,
                pool_pre_ping=True,  # Enable connection health checks
                pool_recycle=3600,   # Recycle connections every hour
                echo=False           # Disable SQL logging in production
            )
            
            # Test connection
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT current_database(), current_user"))
                db_info = result.fetchone()
                
                if not db_info:
                    raise DatabaseConnectionError("Failed to retrieve database information")
                
            print(f"✅ Connection successful!")
            print(f"   Database: {db_info[0]}")
            print(f"   User: {db_info[1]}")
            
        except Exception as e:
            if self.connection_type == ConnectionType.AWS_LAYERED_DB:
                print(f"❌ AWS connection failed: {e}")
                print("💡 Troubleshooting tips:")
                print("   - Ensure SSH tunnel is running (./connect-db.sh)")
                print("   - Check credentials are correct")
                print("   - Verify tunnel is on localhost:5433")
                print("🔄 Falling back to NeonDB...")
                self._setup_neon_connection()
                self._connect()
            else:
                raise DatabaseConnectionError(f"Failed to connect to {self.connection_type.value}: {e}")
    
    def _discover_schemas(self) -> None:
        """Auto-discover all schemas and tables with error handling"""
        if not self.engine:
            raise DatabaseConnectionError("No active database connection")
            
        print("\n🔍 Auto-discovering database schemas...")
        
        try:
            # Get all user schemas
            schemas_query = """
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            ORDER BY schema_name;
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(schemas_query))
                schema_names = [row[0] for row in result]
            
            # Get table info for each schema
            for schema_name in schema_names:
                tables_query = f"""
                SELECT table_name,
                       (SELECT count(*) FROM information_schema.columns 
                        WHERE table_schema = '{schema_name}' AND table_name = t.table_name) as column_count
                FROM information_schema.tables t
                WHERE table_schema = '{schema_name}' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
                """
                
                with self.engine.connect() as conn:
                    result = conn.execute(text(tables_query))
                    tables = [
                        TableInfo(name=row[0], columns=row[1]) 
                        for row in result
                    ]
                
                self.available_schemas[schema_name] = SchemaInfo(
                    tables=tables,
                    table_count=len(tables)
                )
            
            print(f"✅ Discovered {len(self.available_schemas)} schemas")
                
        except Exception as e:
            print(f"⚠️  Warning: Could not auto-discover schemas: {e}")
            self.available_schemas = {}
    
    def _set_default_schema(self) -> None:
        """Set appropriate default schema based on connection type"""
        if not self.available_schemas:
            return
            
        if self.connection_type == ConnectionType.NEON_DB:
            # For NeonDB, prefer test_berlin_data if available
            if 'test_berlin_data' in self.available_schemas:
                self.current_schema = 'test_berlin_data'
                print(f"🎯 Auto-selected default schema: test_berlin_data")
            elif 'public' in self.available_schemas:
                self.current_schema = 'public'
            else:
                self.current_schema = next(iter(self.available_schemas.keys()))
        else:
            # For AWS LayeredDB, prefer berlin_source_data if available
            if 'berlin_source_data' in self.available_schemas:
                self.current_schema = 'berlin_source_data'
                print(f"🎯 Auto-selected default schema: berlin_source_data")
            elif 'public' in self.available_schemas:
                self.current_schema = 'public'
            else:
                self.current_schema = next(iter(self.available_schemas.keys()))
    
    def _show_connection_summary(self) -> None:
        """Display comprehensive connection summary"""
        if not self.connection_type:
            return
            
        print(f"\n{'='*60}")
        print(f"📊 SMART DB CONNECTOR V3 - CONNECTION SUMMARY")
        print(f"{'='*60}")
        print(f"🔗 Connection Type: {self.connection_type.value}")
        
        if self.tunnel_manager:
            tunnel_status = self.tunnel_manager.get_tunnel_status()
            print(f"🚇 Tunnel Status: {tunnel_status.status} ({tunnel_status.host}:{tunnel_status.port})")
        
        if self.available_schemas:
            print(f"\n🗂️  Discovered {len(self.available_schemas)} schemas:")
            for schema_name, info in self.available_schemas.items():
                status = "🎯 [CURRENT]" if schema_name == self.current_schema else "📁"
                print(f"  {status} {schema_name}: {info.table_count} tables")
                
                # Show sample tables
                if info.table_count > 0:
                    sample_tables = info.tables[:3]
                    for table in sample_tables:
                        print(f"       └─ {table.name} ({table.columns} columns)")
                    if info.table_count > 3:
                        print(f"       └─ ... and {info.table_count - 3} more tables")
        else:
            print("⚠️  No schemas discovered")
        
        print(f"\n💡 Quick Commands:")
        print(f"   db.schemas          # List all schemas")
        print(f"   db.use('schema')    # Switch to schema") 
        print(f"   db.tables           # List tables in current schema")
        print(f"   db.query('sql')     # Execute query")
        print(f"   db.populate(df, 'table')  # Insert DataFrame")
        print(f"   db.health_check()   # Check connection status")
        print(f"{'='*60}")
    
    @property
    def schemas(self) -> List[str]:
        """Get list of available schema names"""
        return list(self.available_schemas.keys())
    
    @property 
    def tables(self) -> List[str]:
        """Get list of tables in current schema"""
        if self.current_schema and self.current_schema in self.available_schemas:
            return [table.name for table in self.available_schemas[self.current_schema].tables]
        return []
    
    def use(self, schema_name: str) -> bool:
        """
        Switch to specified schema
        
        Args:
            schema_name: Name of schema to switch to
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            SchemaError: If schema does not exist
        """
        if schema_name not in self.available_schemas:
            available = ', '.join(self.schemas)
            error_msg = f"Schema '{schema_name}' not found. Available: {available}"
            print(f"❌ {error_msg}")
            return False
        
        old_schema = self.current_schema
        self.current_schema = schema_name
        table_count = len(self.tables)
        print(f"✅ Switched from '{old_schema}' to '{schema_name}' ({table_count} tables)")
        
        if 0 < table_count <= 10:
            print(f"   Tables: {', '.join(self.tables)}")
        
        return True
    
    def query(
        self, 
        sql: str, 
        schema: Optional[str] = None, 
        show_info: bool = True
    ) -> pd.DataFrame:
        """
        Execute SQL query with smart schema handling and error recovery
        
        Args:
            sql: SQL query string
            schema: Optional schema name (uses current if not specified)
            show_info: Whether to show query execution info
            
        Returns:
            pandas.DataFrame: Query results
            
        Raises:
            DatabaseConnectionError: If no active connection
            ValueError: If SQL query is invalid
        """
        if not self.engine:
            raise DatabaseConnectionError("No active database connection")
            
        if not sql or not sql.strip():
            raise ValueError("SQL query cannot be empty")
            
        target_schema = schema or self.current_schema
        
        if show_info and target_schema:
            print(f"🔍 Executing query in schema: '{target_schema}'")
        
        try:
            with self.engine.connect() as conn:
                # Set search path if schema specified
                if target_schema and target_schema != 'public':
                    conn.execute(text(f"SET search_path TO {target_schema}, public"))
                
                result = conn.execute(text(sql))
                
                # Handle DDL statements (CREATE, DROP, etc.) that don't return rows
                if result.returns_rows:
                    df = pd.DataFrame(result.fetchall(), columns=result.keys())
                    if show_info:
                        print(f"✅ Query completed: {len(df)} rows, {len(df.columns)} columns")
                    return df
                else:
                    # DDL statement executed successfully
                    if show_info:
                        print(f"✅ DDL statement executed successfully")
                    return pd.DataFrame()  # Return empty DataFrame for DDL statements
                
        except Exception as e:
            error_msg = f"Query execution failed: {e}"
            print(f"❌ {error_msg}")
            raise RuntimeError(error_msg) from e
    
    def insert(
        self, 
        df: pd.DataFrame, 
        table_name: str, 
        schema: Optional[str] = None,
        if_exists: str = 'replace'
    ) -> Dict[str, Any]:
        """
        Insert DataFrame into table with comprehensive error handling
        
        Args:
            df: DataFrame to insert
            table_name: Target table name
            schema: Schema name (uses current if not specified) 
            if_exists: Action if table exists ('replace', 'append', 'fail')
            
        Returns:
            Dict: Insert operation results
            
        Raises:
            DatabaseConnectionError: If no active connection
            ValueError: If DataFrame is empty or invalid parameters
        """
        if not self.engine:
            raise DatabaseConnectionError("No active database connection")
            
        if df.empty:
            raise ValueError("DataFrame cannot be empty")
            
        if not table_name or not table_name.strip():
            raise ValueError("Table name cannot be empty")
            
        if if_exists not in ['replace', 'append', 'fail']:
            raise ValueError("if_exists must be 'replace', 'append', or 'fail'")
        
        target_schema = schema or self.current_schema
        
        print(f"📝 Inserting {len(df)} rows × {len(df.columns)} columns")
        print(f"   Target: {target_schema}.{table_name}")
        print(f"   Action: {if_exists}")
        
        try:
            # Insert data using pandas to_sql with optimized settings
            df.to_sql(
                name=table_name,
                con=self.engine,
                schema=target_schema,
                if_exists=if_exists,
                index=False,
                method='multi',  # Use multi-row insert for better performance
                chunksize=1000   # Process in chunks for memory efficiency
            )
            
            print(f"✅ Insert completed successfully")
            
            # Refresh schema info
            if target_schema:
                self._refresh_schema_info(target_schema)
            
            return {
                'status': 'success',
                'rows_inserted': len(df),
                'table': f"{target_schema}.{table_name}",
                'schema': target_schema
            }
            
        except Exception as e:
            error_msg = f"Insert operation failed: {e}"
            print(f"❌ {error_msg}")
            return {
                'status': 'error',
                'error': error_msg
            }
    
    def populate(
        self, 
        df: pd.DataFrame, 
        table_name: Optional[str] = None, 
        schema: Optional[str] = None,
        mode: str = 'replace',
        primary_key: Optional[List[str]] = None,
        create_table: bool = True,
        show_report: bool = True
    ) -> Dict[str, Any]:
        """
        Smart populate method with schema prompts, reporting, and advanced options
        
        Features:
        - Interactive schema selection if not provided
        - Comprehensive data analysis and reporting
        - Multiple population modes: replace, append, upsert
        - Automatic table creation with optimal data types
        - Data validation and quality checks
        
        Args:
            df: DataFrame to insert
            table_name: Target table name (will prompt if None)
            schema: Schema name (will prompt if None)
            mode: Population mode ('replace', 'append', 'upsert')
            primary_key: List of columns for upsert operations
            create_table: Whether to create table if not exists
            show_report: Whether to show detailed report
            
        Returns:
            Dict: Comprehensive population operation results
        """
        if not self.engine:
            raise DatabaseConnectionError("No active database connection")
            
        if df.empty:
            raise ValueError("DataFrame cannot be empty")
        
        # Interactive schema selection if not provided
        target_schema = self._get_target_schema(schema)
        
        # Interactive table name if not provided
        target_table = self._get_target_table(table_name, target_schema)
        
        # Generate comprehensive pre-population report
        if show_report:
            self._show_pre_population_report(df, target_table, target_schema, mode)
        
        # Execute population based on mode
        try:
            if mode.lower() == 'upsert':
                return self._upsert_data(df, target_table, target_schema, primary_key, create_table, show_report)
            elif mode.lower() == 'append':
                return self._append_data(df, target_table, target_schema, create_table, show_report)
            else:  # replace mode
                return self._replace_data(df, target_table, target_schema, create_table, show_report)
                
        except Exception as e:
            error_msg = f"Population failed: {e}"
            print(f"❌ {error_msg}")
            return {
                'status': 'error',
                'error': error_msg,
                'table': f"{target_schema}.{target_table}",
                'mode': mode
            }
    
    def _get_target_schema(self, schema: Optional[str] = None) -> str:
        """Get target schema with interactive selection if needed"""
        if schema:
            if schema in self.available_schemas:
                return schema
            else:
                available = ', '.join(self.schemas)
                raise ValueError(f"Schema '{schema}' not found. Available: {available}")
        
        # Interactive schema selection
        print(f"\n🗂️  SCHEMA SELECTION")
        print(f"   Available schemas: {self.schemas}")
        print(f"   Current schema: {self.current_schema}")
        
        schema_choice = input(f"   Select schema (press Enter for '{self.current_schema}'): ").strip()
        
        if not schema_choice:
            return self.current_schema
        elif schema_choice in self.schemas:
            return schema_choice
        else:
            print(f"   ⚠️  Invalid schema '{schema_choice}', using current: {self.current_schema}")
            return self.current_schema
    
    def _get_target_table(self, table_name: Optional[str], schema: str) -> str:
        """Get target table name with validation"""
        if table_name:
            return table_name
        
        # Interactive table name input
        print(f"\n📋 TABLE NAME REQUIRED")
        table_name = input(f"   Enter table name for population: ").strip()
        
        if not table_name:
            raise ValueError("Table name is required")
        
        return table_name
    
    def _show_pre_population_report(self, df: pd.DataFrame, table_name: str, schema: str, mode: str) -> None:
        """Show comprehensive pre-population analysis report"""
        print(f"\n{'='*60}")
        print(f"📊 SMART POPULATE - PRE-POPULATION ANALYSIS")
        print(f"{'='*60}")
        
        print(f"🎯 Target: {schema}.{table_name}")
        print(f"📝 Mode: {mode.upper()}")
        print(f"🔗 Connection: {self.connection_type}")
        
        # DataFrame analysis
        print(f"\n📋 DATASET ANALYSIS:")
        print(f"   Rows: {len(df):,}")
        print(f"   Columns: {len(df.columns)}")
        print(f"   Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
        
        # Column analysis
        print(f"\n🔍 COLUMN ANALYSIS:")
        for col in df.columns:
            dtype = str(df[col].dtype)
            null_count = df[col].isnull().sum()
            null_pct = (null_count / len(df)) * 100
            unique_count = df[col].nunique()
            
            print(f"   {col}: {dtype} | Nulls: {null_count} ({null_pct:.1f}%) | Unique: {unique_count}")
        
        # Data quality checks
        print(f"\n✅ DATA QUALITY CHECKS:")
        total_nulls = df.isnull().sum().sum()
        duplicate_rows = df.duplicated().sum()
        
        print(f"   Total null values: {total_nulls:,}")
        print(f"   Duplicate rows: {duplicate_rows:,}")
        
        if duplicate_rows > 0:
            print(f"   ⚠️  Found {duplicate_rows} duplicate rows - consider deduplication")
        
        # Table existence check
        table_exists = table_name in self.tables
        print(f"\n🏗️  TABLE STATUS:")
        print(f"   Table exists: {'Yes' if table_exists else 'No'}")
        
        if table_exists:
            try:
                existing_count = self.query(f"SELECT COUNT(*) as count FROM {table_name}", schema=schema, show_info=False)
                current_rows = existing_count.iloc[0]['count']
                print(f"   Current rows: {current_rows:,}")
                
                if mode.lower() == 'append':
                    print(f"   Final rows after append: {current_rows + len(df):,}")
                elif mode.lower() == 'replace':
                    print(f"   Final rows after replace: {len(df):,}")
            except:
                print(f"   ⚠️  Could not get current row count")
        
        print(f"{'='*60}")
    
    def _replace_data(self, df: pd.DataFrame, table_name: str, schema: str, 
                     create_table: bool, show_report: bool) -> Dict[str, Any]:
        """Replace all data in table"""
        start_time = time.time()
        
        try:
            # Use enhanced insert method
            result = self.insert(df, table_name, schema, if_exists='replace')
            
            if show_report and result['status'] == 'success':
                self._show_post_population_report(result, 'replace', time.time() - start_time)
            
            return result
            
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'mode': 'replace'}
    
    def _append_data(self, df: pd.DataFrame, table_name: str, schema: str, 
                    create_table: bool, show_report: bool) -> Dict[str, Any]:
        """Append data to existing table"""
        start_time = time.time()
        
        try:
            # Use enhanced insert method
            result = self.insert(df, table_name, schema, if_exists='append')
            
            if show_report and result['status'] == 'success':
                self._show_post_population_report(result, 'append', time.time() - start_time)
            
            return result
            
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'mode': 'append'}
    
    def _upsert_data(self, df: pd.DataFrame, table_name: str, schema: str, 
                    primary_key: Optional[List[str]], create_table: bool, 
                    show_report: bool) -> Dict[str, Any]:
        """Upsert data (insert or update on conflict)"""
        start_time = time.time()
        
        if not primary_key:
            # Try to detect primary key automatically
            primary_key = self._detect_primary_key(df, table_name, schema)
        
        if not primary_key:
            print("⚠️  No primary key specified for upsert, falling back to append mode")
            return self._append_data(df, table_name, schema, create_table, show_report)
        
        try:
            # Check if table exists directly in database
            table_exists = self._table_exists(table_name, schema)
            print(f"🔍 Table exists check: {table_exists}, create_table: {create_table}")
            
            if not table_exists and create_table:
                # Create table first
                self._create_optimized_table(df, table_name, schema, primary_key)
                # Refresh schema info to reflect new table
                self._refresh_schema_info(schema)
            
            # Perform upsert using PostgreSQL ON CONFLICT or equivalent
            upserted_rows = self._execute_upsert(df, table_name, schema, primary_key)
            
            result = {
                'status': 'success',
                'rows_upserted': upserted_rows,
                'table': f"{schema}.{table_name}",
                'schema': schema,
                'mode': 'upsert',
                'primary_key': primary_key
            }
            
            if show_report:
                self._show_post_population_report(result, 'upsert', time.time() - start_time)
            
            self._refresh_schema_info(schema)
            return result
            
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'mode': 'upsert'}
    
    def _table_exists(self, table_name: str, schema: str) -> bool:
        """Check if table exists in database directly (not cached)"""
        try:
            check_sql = """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = :schema AND table_name = :table_name
            )
            """
            with self.engine.connect() as conn:
                result = conn.execute(text(check_sql), {'schema': schema, 'table_name': table_name})
                return result.scalar()
        except Exception:
            return False
    
    def _detect_primary_key(self, df: pd.DataFrame, table_name: str, schema: str) -> Optional[List[str]]:
        """Try to detect primary key columns automatically"""
        # Look for common primary key column names
        pk_candidates = ['id', 'pk', 'primary_key', f'{table_name}_id']
        
        for col in df.columns:
            col_lower = col.lower()
            if col_lower in pk_candidates or col_lower.endswith('_id'):
                # Check if values are unique
                if df[col].nunique() == len(df) and df[col].notna().all():
                    print(f"🔑 Auto-detected primary key: {col}")
                    return [col]
        
        print("🔍 No obvious primary key found, you may specify primary_key parameter")
        return None
    
    def _create_optimized_table(self, df: pd.DataFrame, table_name: str, schema: str, primary_key: List[str]) -> None:
        """Create table with optimized data types and constraints"""
        print(f"🏗️  Creating optimized table: {schema}.{table_name}")
        
        # Generate CREATE TABLE statement
        create_sql = self._generate_create_table_sql(df, table_name, schema, primary_key)
        
        # Execute table creation
        with self.engine.connect() as conn:
            conn.execute(text(create_sql))
            conn.commit()
        
        print(f"✅ Table created successfully")
    
    def _generate_create_table_sql(self, df: pd.DataFrame, table_name: str, schema: str, primary_key: List[str]) -> str:
        """Generate optimized CREATE TABLE SQL"""
        lines = [f"CREATE TABLE IF NOT EXISTS {schema}.{table_name} ("]
        
        # Add columns with optimized types
        for col in df.columns:
            col_type = self._get_optimal_column_type(df[col])
            not_null = "NOT NULL" if col in primary_key else ""
            lines.append(f"    {col} {col_type} {not_null},")
        
        # Add primary key constraint
        if primary_key:
            pk_cols = ', '.join(primary_key)
            lines.append(f"    CONSTRAINT pk_{table_name} PRIMARY KEY ({pk_cols})")
        
        lines.append(");")
        
        return '\n'.join(lines)
    
    def _get_optimal_column_type(self, series: pd.Series) -> str:
        """Determine optimal PostgreSQL column type for a pandas Series"""
        dtype = str(series.dtype)
        
        if 'int' in dtype:
            max_val = series.max() if not series.empty else 0
            if max_val <= 2147483647:  # 32-bit int
                return 'INTEGER'
            else:
                return 'BIGINT'
        elif 'float' in dtype:
            return 'DECIMAL(15,6)'
        elif 'bool' in dtype:
            return 'BOOLEAN'
        elif 'datetime' in dtype:
            return 'TIMESTAMP'
        elif 'object' in dtype:
            max_len = series.astype(str).str.len().max() if not series.empty else 50
            if max_len <= 255:
                return f'VARCHAR({min(max_len * 2, 255)})'
            else:
                return 'TEXT'
        else:
            return 'TEXT'
    
    def _execute_upsert(self, df: pd.DataFrame, table_name: str, schema: str, primary_key: List[str]) -> int:
        """Execute PostgreSQL upsert using ON CONFLICT"""
        pk_cols = ', '.join(primary_key)
        update_cols = [col for col in df.columns if col not in primary_key]
        
        # Create temporary table for batch upsert
        temp_table = f"temp_{table_name}_{int(time.time())}"
        
        try:
            # Insert data to temporary table
            df.to_sql(temp_table, self.engine, schema=schema, if_exists='replace', index=False)
            
            # Generate upsert SQL
            update_set = ', '.join([f"{col} = EXCLUDED.{col}" for col in update_cols])
            
            upsert_sql = f"""
            INSERT INTO {schema}.{table_name} 
            SELECT * FROM {schema}.{temp_table}
            ON CONFLICT ({pk_cols}) 
            DO UPDATE SET {update_set}
            """
            
            # Execute upsert
            with self.engine.connect() as conn:
                result = conn.execute(text(upsert_sql))
                conn.commit()
                
                # Clean up temporary table
                conn.execute(text(f"DROP TABLE {schema}.{temp_table}"))
                conn.commit()
            
            return len(df)  # Return number of rows processed
            
        except Exception as e:
            # Clean up temp table on error
            try:
                with self.engine.connect() as conn:
                    conn.execute(text(f"DROP TABLE IF EXISTS {schema}.{temp_table}"))
                    conn.commit()
            except:
                pass
            raise e
    
    def _show_post_population_report(self, result: Dict[str, Any], mode: str, execution_time: float) -> None:
        """Show comprehensive post-population report"""
        print(f"\n{'='*60}")
        print(f"🎉 SMART POPULATE - OPERATION COMPLETED")
        print(f"{'='*60}")
        
        print(f"✅ Status: {result['status'].upper()}")
        print(f"🎯 Table: {result['table']}")
        print(f"📝 Mode: {mode.upper()}")
        print(f"⏱️  Execution time: {execution_time:.2f} seconds")
        
        if mode == 'upsert':
            print(f"🔄 Rows upserted: {result.get('rows_upserted', 0):,}")
            if 'primary_key' in result:
                print(f"🔑 Primary key: {', '.join(result['primary_key'])}")
        else:
            rows_key = 'rows_inserted' if 'rows_inserted' in result else 'rows_upserted'
            print(f"📊 Rows processed: {result.get(rows_key, 0):,}")
        
        # Performance metrics
        rows_per_second = result.get('rows_inserted', result.get('rows_upserted', 0)) / execution_time if execution_time > 0 else 0
        print(f"⚡ Performance: {rows_per_second:,.0f} rows/second")
        
        print(f"{'='*60}\n")

    def get_table_info(self, table_name: str, schema: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information about a specific table
        
        Args:
            table_name: Name of the table
            schema: Schema name (uses current if not specified)
            
        Returns:
            Dict: Table information including columns and metadata
        """
        if not self.engine:
            raise DatabaseConnectionError("No active database connection")
            
        target_schema = schema or self.current_schema
        
        try:
            columns_query = f"""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = '{target_schema}' AND table_name = '{table_name}'
            ORDER BY ordinal_position;
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(columns_query))
                columns = [dict(row._mapping) for row in result]
            
            return {
                'schema': target_schema,
                'table': table_name,
                'columns': columns,
                'column_count': len(columns)
            }
            
        except Exception as e:
            error_msg = f"Error getting table info: {e}"
            print(f"❌ {error_msg}")
            return {}
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check with detailed diagnostics
        
        Returns:
            Dict: Comprehensive health status information
        """
        if not self.engine or not self.connection_type:
            return {
                'status': 'unhealthy',
                'connection_type': 'unknown',
                'error': 'No database connection established',
                'connection': 'failed'
            }
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1, current_database(), version()"))
                db_info = result.fetchone()
                
                if not db_info:
                    raise DatabaseConnectionError("Unable to retrieve database information")
            
            health_info = {
                'status': 'healthy',
                'connection_type': self.connection_type.value,
                'database': db_info[1],
                'version': db_info[2][:50] + '...' if len(db_info[2]) > 50 else db_info[2],
                'schemas_available': len(self.available_schemas),
                'current_schema': self.current_schema,
                'tables_in_current_schema': len(self.tables),
                'connection': 'active'
            }
            
            # Add tunnel status if using AWS
            if self.tunnel_manager:
                tunnel_status = self.tunnel_manager.get_tunnel_status()
                health_info['tunnel_status'] = tunnel_status.status
                health_info['tunnel_active'] = tunnel_status.active
            
            return health_info
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'connection_type': self.connection_type.value,
                'error': str(e),
                'connection': 'failed'
            }
    
    def _refresh_schema_info(self, schema_name: str) -> None:
        """
        Refresh table information for specific schema
        
        Args:
            schema_name: Name of schema to refresh
        """
        if not self.engine:
            return
            
        if schema_name not in self.available_schemas:
            self.available_schemas[schema_name] = SchemaInfo(tables=[], table_count=0)
            
        try:
            tables_query = f"""
            SELECT table_name,
                   (SELECT count(*) FROM information_schema.columns 
                    WHERE table_schema = '{schema_name}' AND table_name = t.table_name) as column_count
            FROM information_schema.tables t
            WHERE table_schema = '{schema_name}' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(tables_query))
                tables = [
                    TableInfo(name=row[0], columns=row[1]) 
                    for row in result
                ]
            
            self.available_schemas[schema_name] = SchemaInfo(
                tables=tables,
                table_count=len(tables)
            )
        except Exception as e:
            print(f"Warning: Could not refresh schema info: {e}")
    
    def show_connection_info(self) -> None:
        """Show current connection information"""
        self._show_connection_summary()
    
    def close(self) -> None:
        """Close database connection and cleanup resources"""
        if self.engine:
            self.engine.dispose()
            print("🔒 Database connection closed")
            self.engine = None


# Convenient aliases for easy import and usage
db_connector = SmartDbConnectorV3


def quick_connect(
    database: Optional[str] = None, 
    username: Optional[str] = None, 
    password: Optional[str] = None
) -> SmartDbConnectorV3:
    """
    Quick connection function for immediate use
    
    Args:
        database: Target database ('layereddb' for AWS, None for NeonDB)
        username: Database username (for AWS connection)
        password: Database password (for AWS connection)
        
    Returns:
        SmartDbConnectorV3: Connected database instance
        
    Raises:
        DatabaseConnectionError: If connection fails
    """
    return SmartDbConnectorV3(database, username, password, auto_discover=True)


def demo_usage() -> None:
    """Demonstrate usage of Smart DB Connector V3"""
    print("🎯 SMART DB CONNECTOR V3 - USAGE EXAMPLES")
    print("=" * 50)
    
    print("\n1. Default NeonDB connection:")
    print("   db = db_connector()")
    print("   # Connects to NeonDB, auto-switches to test_berlin_data schema")
    
    print("\n2. AWS LayeredDB connection with credentials:")
    print("   db = db_connector('layereddb', 'your_username', 'your_password')")
    print("   # Connects to AWS LayeredDB through SSH tunnel")
    
    print("\n3. AWS LayeredDB with interactive credentials:")
    print("   db = db_connector('layereddb')")
    print("   # Will prompt for username and password")
    
    print("\n4. Basic operations:")
    print("   db.schemas              # List available schemas")
    print("   db.use('schema_name')   # Switch to specific schema")
    print("   db.tables               # List tables in current schema")
    print("   df = db.query('SELECT * FROM table')  # Execute query")
    print("   db.populate(df, 'new_table')         # Insert data")
    print("   db.health_check()       # Check connection status")
    
    print("\n5. Error handling:")
    print("   try:")
    print("       db.use('nonexistent')")
    print("   except SchemaError as e:")
    print("       print(f'Schema error: {e}')")


if __name__ == "__main__":
    demo_usage()