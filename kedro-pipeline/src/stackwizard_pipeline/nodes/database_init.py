"""
Database initialization nodes for test pipeline
"""
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pathlib import Path
from typing import Dict, Any, List
import os
import time
import logging

logger = logging.getLogger(__name__)


def create_test_database(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create an empty test database"""
    
    # Handle both direct database params and nested params
    if "database" in params:
        db_config = params.get("database", {})
    else:
        db_config = params
    host = db_config.get("host", "localhost")
    port = db_config.get("port", 5432)
    admin_user = db_config.get("admin_user", "postgres")
    admin_password = db_config.get("admin_password", "postgres")
    test_db_name = db_config.get("test_db_name", "stackwizard_test")
    test_user = db_config.get("test_user", "stackwizard_user")
    test_password = db_config.get("test_password", "stackwizard_pass")
    
    result = {
        "database_created": False,
        "user_created": False,
        "errors": [],
        "warnings": []
    }
    
    try:
        # Connect to PostgreSQL as admin
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=admin_user,
            password=admin_password,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Drop database if exists (for clean tests)
        if params.get("clean_start", True):
            try:
                cur.execute(f"DROP DATABASE IF EXISTS {test_db_name}")
                result["warnings"].append(f"Dropped existing database {test_db_name}")
            except Exception as e:
                result["warnings"].append(f"Could not drop database: {str(e)}")
        
        # Create database
        try:
                cur.execute(
                    sql.SQL("DROP DATABASE IF EXISTS {}").format(
                        sql.Identifier(test_db_name)
                    )
                )
                result["warnings"].append(f"Dropped existing database {test_db_name}")
            except Exception as e:
                result["warnings"].append(f"Could not drop database: {str(e)}")
        
        # Create database
        try:
            cur.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(test_db_name)
                )
            )
            result["database_created"] = True
            logger.info(f"Created database {test_db_name}")
        except psycopg2.errors.DuplicateDatabase:
            result["warnings"].append(f"Database {test_db_name} already exists")
            result["database_created"] = True
        
        # Create user if not exists
        try:
            cur.execute(f"CREATE USER {test_user} WITH PASSWORD '{test_password}'")
            result["user_created"] = True
            logger.info(f"Created user {test_user}")
        except psycopg2.errors.DuplicateObject:
            result["warnings"].append(f"User {test_user} already exists")
            result["user_created"] = True
        
        # Grant privileges
        cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {test_db_name} TO {test_user}")
        
        cur.close()
        conn.close()
        
        result["success"] = True
        result["connection_string"] = f"postgresql://{test_user}:{test_password}@{host}:{port}/{test_db_name}"
        
    except Exception as e:
        result["success"] = False
        result["errors"].append(str(e))
        logger.error(f"Failed to create database: {str(e)}")
    
    return result


def load_sql_schema(db_info: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    """Load SQL schema files into the database"""
    
    if not db_info.get("success"):
        return {
            "success": False,
            "error": "Database creation failed",
            "tables_created": []
        }
    
    result = {
        "tables_created": [],
        "indexes_created": [],
        "errors": [],
        "warnings": []
    }
    
    # Get SQL files path
    sql_path = Path(params.get("sql_path", "data/01_raw/sql"))
    schema_path = sql_path / "schema"
    
    if not schema_path.exists():
        result["errors"].append(f"Schema path not found: {schema_path}")
        result["success"] = False
        return result
    
    # Get all schema SQL files sorted by name
    schema_files = sorted(schema_path.glob("*.sql"))
    
    if not schema_files:
        result["warnings"].append("No schema files found")
    
    # Connect to the test database
    try:
        conn = psycopg2.connect(db_info["connection_string"])
        cur = conn.cursor()
        
        for sql_file in schema_files:
            try:
                logger.info(f"Executing {sql_file.name}")
                with open(sql_file, 'r') as f:
                    sql_content = f.read()
                    cur.execute(sql_content)
                    
                # Extract table name from filename
                table_name = sql_file.stem.replace("001_create_", "").replace("002_create_", "").replace("003_create_", "")
                result["tables_created"].append(table_name)
                
            except Exception as e:
                result["errors"].append(f"Error executing {sql_file.name}: {str(e)}")
                logger.error(f"Failed to execute {sql_file.name}: {str(e)}")
        
        conn.commit()
        
        # Verify tables were created
        cur.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        actual_tables = [row[0] for row in cur.fetchall()]
        
        result["actual_tables"] = actual_tables
        result["success"] = len(result["errors"]) == 0
        
        cur.close()
        conn.close()
        
    except Exception as e:
        result["success"] = False
        result["errors"].append(f"Database connection failed: {str(e)}")
        logger.error(f"Failed to load schema: {str(e)}")
    
    return result


def load_seed_data(schema_info: Dict[str, Any], db_info: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    """Load seed data into the database"""
    
    if not schema_info.get("success"):
        return {
            "success": False,
            "error": "Schema creation failed",
            "records_inserted": {}
        }
    
    result = {
        "records_inserted": {},
        "errors": [],
        "warnings": []
    }
    
    # Determine which data to load based on params
    data_type = params.get("data_type", "seed")  # "seed" or "test"
    sql_path = Path(params.get("sql_path", "data/01_raw/sql"))
    data_path = sql_path / data_type
    
    if not data_path.exists():
        result["errors"].append(f"Data path not found: {data_path}")
        result["success"] = False
        return result
    
    # Get all data SQL files sorted by name
    data_files = sorted(data_path.glob("*.sql"))
    
    if not data_files:
        result["warnings"].append(f"No {data_type} data files found")
    
    # Connect to the test database
    try:
        conn = psycopg2.connect(db_info["connection_string"])
        cur = conn.cursor()
        
        for sql_file in data_files:
            try:
                logger.info(f"Loading data from {sql_file.name}")
                with open(sql_file, 'r') as f:
                    sql_content = f.read()
                    cur.execute(sql_content)
                    
                # Track rows inserted
                if cur.rowcount > 0:
                    table_name = sql_file.stem.replace(f"001_{data_type}_", "").replace(f"002_{data_type}_", "")
                    result["records_inserted"][table_name] = cur.rowcount
                
            except Exception as e:
                result["errors"].append(f"Error loading {sql_file.name}: {str(e)}")
                logger.error(f"Failed to load {sql_file.name}: {str(e)}")
        
        conn.commit()
        
        # Verify data was loaded
        for table in ['users', 'items']:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            result[f"{table}_count"] = count
        
        result["success"] = len(result["errors"]) == 0
        
        cur.close()
        conn.close()
        
    except Exception as e:
        result["success"] = False
        result["errors"].append(f"Database connection failed: {str(e)}")
        logger.error(f"Failed to load data: {str(e)}")
    
    return result


def verify_database(data_info: Dict[str, Any], db_info: Dict[str, Any]) -> Dict[str, Any]:
    """Verify the database is properly initialized with data"""
    
    if not data_info.get("success"):
        return {
            "success": False,
            "error": "Data loading failed"
        }
    
    result = {
        "tables": {},
        "constraints": {},
        "indexes": {},
        "errors": [],
        "warnings": []
    }
    
    try:
        conn = psycopg2.connect(db_info["connection_string"])
        cur = conn.cursor()
        
        # Check tables and row counts
        tables_to_check = ['users', 'items', 'sessions']
        for table in tables_to_check:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            result["tables"][table] = {"row_count": count}
        
        # Check foreign key constraints
        cur.execute("""
            SELECT
                tc.table_name, 
                kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name 
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
        """)
        
        constraints = cur.fetchall()
        result["constraints"]["foreign_keys"] = len(constraints)
        
        # Check indexes
        cur.execute("""
            SELECT 
                tablename,
                indexname
            FROM pg_indexes
            WHERE schemaname = 'public'
        """)
        
        indexes = cur.fetchall()
        result["indexes"]["total"] = len(indexes)
        
        # Run test queries
        test_queries = [
            ("User with items", """
                SELECT u.username, COUNT(i.id) as item_count 
                FROM users u 
                LEFT JOIN items i ON u.id = i.owner_id 
                GROUP BY u.username 
                LIMIT 5
            """),
            ("Active items", "SELECT COUNT(*) FROM items WHERE is_available = true"),
            ("Admin users", "SELECT COUNT(*) FROM users WHERE is_superuser = true")
        ]
        
        result["test_queries"] = {}
        for query_name, query in test_queries:
            try:
                cur.execute(query)
                result["test_queries"][query_name] = "OK"
            except Exception as e:
                result["test_queries"][query_name] = f"Failed: {str(e)}"
                result["errors"].append(f"Test query '{query_name}' failed")
        
        result["success"] = len(result["errors"]) == 0
        
        cur.close()
        conn.close()
        
    except Exception as e:
        result["success"] = False
        result["errors"].append(f"Database verification failed: {str(e)}")
        logger.error(f"Failed to verify database: {str(e)}")
    
    return result


def cleanup_test_database(verification_info: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    """Clean up test database after tests"""
    
    if not params.get("cleanup_after_test", False):
        return {
            "success": True,
            "message": "Cleanup skipped (cleanup_after_test is False)"
        }
    
    db_config = params.get("database", {})
    host = db_config.get("host", "localhost")
    port = db_config.get("port", 5432)
    admin_user = db_config.get("admin_user", "postgres")
    admin_password = db_config.get("admin_password", "postgres")
    test_db_name = db_config.get("test_db_name", "stackwizard_test")
    
    result = {
        "database_dropped": False,
        "errors": []
    }
    
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=admin_user,
            password=admin_password,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Terminate connections to the test database
        cur.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{test_db_name}'
            AND pid <> pg_backend_pid()
        """)
        
        # Drop the test database
        cur.execute(f"DROP DATABASE IF EXISTS {test_db_name}")
        result["database_dropped"] = True
        
        cur.close()
        conn.close()
        
        result["success"] = True
        logger.info(f"Dropped test database {test_db_name}")
        
    except Exception as e:
        result["success"] = False
        result["errors"].append(str(e))
        logger.error(f"Failed to cleanup database: {str(e)}")
    
    return result