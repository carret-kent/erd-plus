#!/usr/bin/env python3
"""
MySQL Database Schema Extractor
Connects to MySQL database and extracts table schema information
"""

import mysql.connector
from mysql.connector import Error
from typing import Dict, List, Any

class MySQLSchemaExtractor:
    def __init__(self, config: Dict[str, Any]):
        """Initialize with database configuration"""
        self.config = config
        self.connection = None
        
    def connect(self):
        """Establish connection to MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['username'],
                password=self.config['password']
            )
            if self.connection.is_connected():
                print(f"Successfully connected to MySQL database: {self.config['database']}")
                print(f"Target schema: {self.config.get('schema', self.config['database'])}")
        except Error as e:
            raise Exception(f"Error connecting to MySQL: {e}")
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")
    
    def get_tables(self) -> List[str]:
        """Get all table names from the specified schema"""
        cursor = self.connection.cursor()
        schema_name = self.config.get('schema', self.config['database'])
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = %s", (schema_name,))
        tables = [table[0] for table in cursor.fetchall()]
        cursor.close()
        return tables
    
    def get_table_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """Get column information for a specific table"""
        cursor = self.connection.cursor(dictionary=True)
        schema_name = self.config.get('schema', self.config['database'])
        query = """
        SELECT 
            COLUMN_NAME,
            DATA_TYPE,
            IS_NULLABLE,
            COLUMN_KEY,
            COLUMN_DEFAULT,
            EXTRA,
            CHARACTER_MAXIMUM_LENGTH,
            NUMERIC_PRECISION,
            NUMERIC_SCALE,
            COLUMN_COMMENT
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION
        """
        cursor.execute(query, (schema_name, table_name))
        columns = cursor.fetchall()
        cursor.close()
        return columns
    
    def get_foreign_keys(self) -> List[Dict[str, Any]]:
        """Get foreign key relationships"""
        cursor = self.connection.cursor(dictionary=True)
        schema_name = self.config.get('schema', self.config['database'])
        query = """
        SELECT 
            TABLE_NAME,
            COLUMN_NAME,
            REFERENCED_TABLE_NAME,
            REFERENCED_COLUMN_NAME,
            CONSTRAINT_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
        WHERE TABLE_SCHEMA = %s 
        AND REFERENCED_TABLE_NAME IS NOT NULL
        """
        cursor.execute(query, (schema_name,))
        foreign_keys = cursor.fetchall()
        cursor.close()
        return foreign_keys
    
    def get_indexes(self, table_name: str) -> List[Dict[str, Any]]:
        """Get index information for a specific table"""
        cursor = self.connection.cursor(dictionary=True)
        schema_name = self.config.get('schema', self.config['database'])
        query = """
        SELECT 
            INDEX_NAME,
            COLUMN_NAME,
            NON_UNIQUE,
            SEQ_IN_INDEX
        FROM INFORMATION_SCHEMA.STATISTICS 
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        ORDER BY INDEX_NAME, SEQ_IN_INDEX
        """
        cursor.execute(query, (schema_name, table_name))
        indexes = cursor.fetchall()
        cursor.close()
        return indexes
    
    def extract_schema(self) -> Dict[str, Any]:
        """Extract complete schema information"""
        try:
            self.connect()
            
            schema_name = self.config.get('schema', self.config['database'])
            schema_data = {
                'database': self.config['database'],
                'schema': schema_name,
                'tables': {},
                'relationships': []
            }
            
            # Get all tables
            tables = self.get_tables()
            print(f"Found {len(tables)} tables in schema '{schema_name}': {', '.join(tables)}")
            
            # Extract information for each table
            for table_name in tables:
                print(f"Processing table: {table_name}")
                
                columns = self.get_table_columns(table_name)
                indexes = self.get_indexes(table_name)
                
                schema_data['tables'][table_name] = {
                    'columns': columns,
                    'indexes': indexes
                }
            
            # Get foreign key relationships
            foreign_keys = self.get_foreign_keys()
            schema_data['relationships'] = foreign_keys
            
            print(f"Extracted schema for {len(tables)} tables with {len(foreign_keys)} relationships")
            return schema_data
            
        finally:
            self.disconnect()
