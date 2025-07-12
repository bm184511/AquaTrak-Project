"""Database utility functions for AquaTrak"""

import logging
from typing import Dict, Any, List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from datetime import datetime, date, timedelta
import json

logger = logging.getLogger(__name__)

def execute_raw_sql(db: Session, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Execute raw SQL query and return results as dictionaries"""
    try:
        result = db.execute(text(sql), params or {})
        return [dict(row._mapping) for row in result]
    except Exception as e:
        logger.error(f"SQL execution failed: {e}")
        raise

def get_table_stats(db: Session, table_name: str) -> Dict[str, Any]:
    """Get table statistics"""
    try:
        # Get row count
        count_sql = f"SELECT COUNT(*) as count FROM {table_name}"
        count_result = execute_raw_sql(db, count_sql)
        row_count = count_result[0]['count'] if count_result else 0
        
        # Get table size
        # Check if the table exists before querying pg_total_relation_size
        table_exists_sql = f"""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = '{table_name}'
        );
        """
        table_exists = execute_raw_sql(db, table_exists_sql)[0]['exists']
        
        table_size = {}
        if table_exists:
            size_sql = f"""
            SELECT pg_size_pretty(pg_total_relation_size('{table_name}')) as size,
                   pg_total_relation_size('{table_name}') as size_bytes
            """
            size_result = execute_raw_sql(db, size_sql)
            table_size = size_result[0] if size_result else {}
        else:
            logger.warning(f"Table '{table_name}' does not exist, cannot retrieve size.")
            table_size = {'size': 'N/A', 'size_bytes': 0}

        # Get last updated if 'created_at' column exists
        last_updated = None
        columns_sql = f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = '{table_name}' AND column_name = 'created_at'
        """
        if execute_raw_sql(db, columns_sql):
            last_updated_sql = f"SELECT MAX(created_at) as last_updated FROM {table_name}"
            last_updated_result = execute_raw_sql(db, last_updated_sql)
            last_updated = last_updated_result[0]['last_updated'] if last_updated_result else None
        
        return {
            'table_name': table_name,
            'row_count': row_count,
            'size': table_size.get('size', 'Unknown'),
            'size_bytes': table_size.get('size_bytes', 0),
            'last_updated': last_updated
        }
    except Exception as e:
        logger.error(f"Failed to get stats for table {table_name}: {e}")
        return {
            'table_name': table_name,
            'error': str(e)
        }

def get_database_health(db: Session) -> Dict[str, Any]:
    """Get comprehensive database health information"""
    try:
        # Get database info
        db_info_sql = """
        SELECT 
            current_database() as database_name,
            version() as version,
            current_user as current_user,
            inet_server_addr() as server_address,
            inet_server_port() as server_port
        """
        db_info = execute_raw_sql(db, db_info_sql)[0]
        
        # Get table list
        tables_sql = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
        """
        tables_result = execute_raw_sql(db, tables_sql)
        table_names = [row['table_name'] for row in tables_result]
        
        # Get table statistics
        table_stats = {}
        for table_name in table_names:
            table_stats[table_name] = get_table_stats(db, table_name)
        
        # Get connection info
        connection_sql = """
        SELECT 
            count(*) as active_connections,
            max(backend_start) as oldest_connection
        FROM pg_stat_activity 
        WHERE state = 'active'
        """
        connection_info = execute_raw_sql(db, connection_sql)[0]
        
        return {
            'database_info': db_info,
            'tables': table_names,
            'table_statistics': table_stats,
            'connection_info': connection_info,
            'health_status': 'healthy',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get database health: {e}")
        return {
            'health_status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

def backup_table_data(db: Session, table_name: str, backup_path: str) -> bool:
    """Backup table data to JSON file"""
    try:
        # Get all data from table
        data_sql = f"SELECT * FROM {table_name}"
        data = execute_raw_sql(db, data_sql)
        
        # Convert datetime objects to strings
        for row in data:
            for key, value in row.items():
                if isinstance(value, (datetime, date)):
                    row[key] = value.isoformat()
        
        # Save to JSON file
        with open(backup_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Table {table_name} backed up to {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to backup table {table_name}: {e}")
        return False

def restore_table_data(db: Session, table_name: str, backup_path: str) -> bool:
    """Restore table data from JSON file"""
    try:
        # Read backup data
        with open(backup_path, 'r') as f:
            data = json.load(f)
        
        if not data:
            logger.warning(f"No data found in backup file {backup_path}")
            return False
        
        # Clear existing data
        db.execute(text(f"DELETE FROM {table_name}"))
        
        # Insert backup data
        for row in data:
            # Convert string dates back to datetime
            for key, value in row.items():
                if isinstance(value, str) and 'T' in value:
                    try:
                        row[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    except:
                        pass
            
            # Build INSERT statement
            columns = ', '.join(row.keys())
            placeholders = ', '.join([f':{key}' for key in row.keys()])
            insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            db.execute(text(insert_sql), row)
        
        db.commit()
        logger.info(f"Table {table_name} restored from {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to restore table {table_name}: {e}")
        db.rollback()
        return False

def optimize_table(db: Session, table_name: str) -> bool:
    """Optimize table performance"""
    try:
        # Analyze table
        db.execute(text(f"ANALYZE {table_name}"))
        
        # Vacuum table
        db.execute(text(f"VACUUM {table_name}"))
        
        # Reindex table
        db.execute(text(f"REINDEX TABLE {table_name}"))
        
        logger.info(f"Table {table_name} optimized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to optimize table {table_name}: {e}")
        return False

def get_data_summary(db: Session, module_name: str) -> Dict[str, Any]:
    """Get data summary for a specific module"""
    try:
        # Get data table name
        data_table = f"{module_name.lower().replace(' ', '_')}_data"
        results_table = f"{module_name.lower().replace(' ', '_')}_analysis_results"
        
        summary = {
            'module_name': module_name,
            'data_records': 0,
            'analysis_results': 0,
            'last_data_update': None,
            'last_analysis': None,
            'data_sources': []
        }
        
        # Check if tables exist and get stats
        tables_sql = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name IN (:data_table, :results_table)
        """
        existing_tables = execute_raw_sql(db, tables_sql, {
            'data_table': data_table,
            'results_table': results_table
        })
        
        existing_table_names = [row['table_name'] for row in existing_tables]
        
        if data_table in existing_table_names:
            data_stats = get_table_stats(db, data_table)
            summary['data_records'] = data_stats.get('row_count', 0)
            summary['last_data_update'] = data_stats.get('last_updated')
        
        if results_table in existing_table_names:
            results_stats = get_table_stats(db, results_table)
            summary['analysis_results'] = results_stats.get('row_count', 0)
            summary['last_analysis'] = results_stats.get('last_updated')
        
        return summary
    except Exception as e:
        logger.error(f"Failed to get summary for module {module_name}: {e}")
        return {
            'module_name': module_name,
            'error': str(e)
        }

def cleanup_old_data(db: Session, table_name: str, days_to_keep: int = 90) -> int:
    """Clean up old data from table"""
    try:
        # Check if 'created_at' column exists before attempting to use it
        columns_sql = f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = '{table_name}' AND column_name = 'created_at'
        """
        if not execute_raw_sql(db, columns_sql):
            logger.warning(f"Table '{table_name}' does not have a 'created_at' column. Skipping cleanup.")
            return 0

        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Count records to be deleted
        count_sql = f"SELECT COUNT(*) as count FROM {table_name} WHERE created_at < :cutoff_date"
        count_result = execute_raw_sql(db, count_sql, {'cutoff_date': cutoff_date})
        records_to_delete = count_result[0]['count'] if count_result else 0
        
        if records_to_delete > 0:
            # Delete old records
            delete_sql = f"DELETE FROM {table_name} WHERE created_at < :cutoff_date"
            db.execute(text(delete_sql), {'cutoff_date': cutoff_date})
            db.commit()
            
            logger.info(f"Deleted {records_to_delete} old records from {table_name}")
            return records_to_delete
        else:
            logger.info(f"No old records to delete from {table_name}")
            return 0
    except Exception as e:
        logger.error(f"Failed to cleanup old data from {table_name}: {e}")
        db.rollback()
        return 0

def get_performance_metrics(db: Session) -> Dict[str, Any]:
    """Get database performance metrics"""
    try:
        # Check if pg_stat_statements extension is enabled
        extension_check_sql = "SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'"
        pg_stat_statements_enabled = bool(execute_raw_sql(db, extension_check_sql))

        slow_queries = []
        if pg_stat_statements_enabled:
            # Get slow queries
            slow_queries_sql = """
            SELECT 
                query,
                calls,
                total_time,
                mean_time,
                rows
            FROM pg_stat_statements 
            ORDER BY mean_time DESC 
            LIMIT 10
            """
            slow_queries = execute_raw_sql(db, slow_queries_sql)
        else:
            logger.warning("pg_stat_statements extension is not enabled. Slow query metrics will not be available.")

        # Get table access statistics
        table_stats_sql = """
        SELECT 
            schemaname,
            tablename,
            seq_scan,
            seq_tup_read,
            idx_scan,
            idx_tup_fetch,
            n_tup_ins,
            n_tup_upd,
            n_tup_del
        FROM pg_stat_user_tables 
        ORDER BY n_tup_ins + n_tup_upd + n_tup_del DESC
        """
        table_stats = execute_raw_sql(db, table_stats_sql)
        
        # Get index usage statistics
        index_stats_sql = """
        SELECT 
            schemaname,
            tablename,
            indexname,
            idx_scan,
            idx_tup_read,
            idx_tup_fetch
        FROM pg_stat_user_indexes 
        ORDER BY idx_scan DESC
        """
        index_stats = execute_raw_sql(db, index_stats_sql)
        
        return {
            'slow_queries': slow_queries,
            'table_statistics': table_stats,
            'index_statistics': index_stats,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        return {
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

def validate_data_integrity(db: Session, table_name: str) -> Dict[str, Any]:
    """Validate data integrity for a table"""
    try:
        validation_results = {
            'table_name': table_name,
            'checks': {},
            'status': 'valid'
        }
        
        # Get column names to construct dynamic queries
        columns_info_sql = f"""
        SELECT column_name, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = '{table_name}'
        ORDER BY ordinal_position
        """
        columns_info = execute_raw_sql(db, columns_info_sql)
        column_names = [col['column_name'] for col in columns_info]
        nullable_columns = {col['column_name'] for col in columns_info if col['is_nullable'] == 'YES'}
        
        # Check for null values in non-nullable fields
        null_issues = []
        for col in columns_info:
            if col['is_nullable'] == 'NO':
                null_check_sql = f"SELECT COUNT(*) as null_count FROM {table_name} WHERE {col['column_name']} IS NULL"
                null_count_result = execute_raw_sql(db, null_check_sql)
                if null_count_result and null_count_result[0]['null_count'] > 0:
                    null_issues.append({'column_name': col['column_name'], 'null_count': null_count_result[0]['null_count']})
        
        validation_results['checks']['null_values'] = {
            'status': 'passed' if not null_issues else 'failed',
            'details': null_issues
        }
        
        # Check for duplicate records
        # This check might be very slow on large tables without a primary key or unique index
        if column_names: # Only run if table has columns
            group_by_cols = ', '.join(f'"{col}"' for col in column_names) # Quote column names to handle reserved words
            duplicate_check_sql = f"""
            SELECT COUNT(*) as duplicate_count
            FROM (
                SELECT {group_by_cols}, COUNT(*) as cnt
                FROM {table_name}
                GROUP BY {group_by_cols}
                HAVING COUNT(*) > 1
            ) duplicates
            """
            
            try:
                duplicate_results = execute_raw_sql(db, duplicate_check_sql)
                duplicate_count = duplicate_results[0]['duplicate_count'] if duplicate_results else 0
                validation_results['checks']['duplicates'] = {
                    'status': 'passed' if duplicate_count == 0 else 'failed',
                    'count': duplicate_count
                }
            except Exception as e:
                logger.warning(f"Could not check for duplicates on {table_name} due to error (might lack primary key): {e}")
                validation_results['checks']['duplicates'] = {
                    'status': 'skipped_or_error',
                    'error': str(e)
                }
        else:
            validation_results['checks']['duplicates'] = {
                'status': 'skipped',
                'details': 'Table has no columns defined.'
            }


        # Check for orphaned records (assuming 'users' table and 'user_id' foreign key)
        if 'user_id' in column_names:
            orphan_check_sql = f"""
            SELECT COUNT(*) as orphan_count
            FROM {table_name} t
            LEFT JOIN users u ON t.user_id = u.id
            WHERE u.id IS NULL AND t.user_id IS NOT NULL
            """
            
            try:
                orphan_results = execute_raw_sql(db, orphan_check_sql)
                orphan_count = orphan_results[0]['orphan_count'] if orphan_results else 0
                validation_results['checks']['orphaned_records'] = {
                    'status': 'passed' if orphan_count == 0 else 'failed',
                    'count': orphan_count
                }
            except Exception as e:
                validation_results['checks']['orphaned_records'] = {
                    'status': 'error',
                    'error': str(e)
                }
        else:
            validation_results['checks']['orphaned_records'] = {
                'status': 'skipped',
                'details': 'Table does not have a "user_id" column for orphan check.'
            }
        
        # Overall status
        failed_checks = [check for check in validation_results['checks'].values() if check.get('status') == 'failed']
        if failed_checks:
            validation_results['status'] = 'invalid'
        
        return validation_results
    except Exception as e:
        logger.error(f"Failed to validate data integrity for {table_name}: {e}")
        return {
            'table_name': table_name,
            'status': 'error',
            'error': str(e)
        }