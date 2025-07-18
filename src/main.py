#!/usr/bin/env python3
"""
ERD Plus - MySQL Schema to ERD Generator
Main entry point for the application
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from db_connector import MySQLSchemaExtractor
from erd_generator import ERDGenerator
from markdown_converter import MarkdownConverter
from test_simple import test_mysql_connection

def load_config():
    """Load database configuration from .env file"""
    # Load .env file from the same directory as this script
    env_path = Path(__file__).parent / '.env'
    
    if not env_path.exists():
        print(f"Error: Configuration file {env_path} not found")
        print("Please copy .env.example to .env and configure your database settings")
        sys.exit(1)
    
    load_dotenv(env_path)
    
    config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', '3306')),
        'database': os.getenv('DB_DATABASE'),
        'username': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD', ''),
        'schema': os.getenv('DB_SCHEMA')
    }
    
    # Validate required fields
    required_fields = ['host', 'database', 'username', 'schema']
    missing_fields = [field for field in required_fields if not config[field]]
    
    if missing_fields:
        print(f"Error: Missing required configuration fields in .env: {', '.join(missing_fields)}")
        sys.exit(1)
    
    return config

def main():
    """Main application logic"""
    print("ERD Plus - Starting MySQL Schema to ERD Generation")
    
    # Load configuration
    config = load_config()
    
    # 0. Test database connection first
    print("0. Testing database connection...")
    if not test_mysql_connection(config, verbose=True):
        print("❌ Database connection test failed. Please check your configuration.")
        sys.exit(1)
    print("✅ Database connection test passed!\n")
    
    # Create output directory structure: /data/output/{database}/
    database_name = config['database']
    schema_name = config['schema']
    output_base_dir = Path("/data/output")
    output_dir = output_base_dir / database_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 1. Extract schema from MySQL database
        print("1. Connecting to MySQL database and extracting schema...")
        extractor = MySQLSchemaExtractor(config)
        schema_data = extractor.extract_schema()
        
        # 2. Generate ERD file
        print("2. Generating ERD file...")
        erd_generator = ERDGenerator(schema_data)
        erd_file_path = output_dir / f"{schema_name}.er"
        erd_generator.generate_erd_file(erd_file_path)
        
        # 3. Generate ER diagram using Haskell ERD
        print("3. Generating ER diagram...")
        pdf_path = output_dir / f"{schema_name}.pdf"
        erd_generator.generate_diagram(erd_file_path, pdf_path)
        
        # 4. Convert ERD to Markdown
        print("4. Converting ERD to Markdown...")
        converter = MarkdownConverter()
        markdown_path = output_dir / f"{schema_name}.md"
        converter.convert_erd_to_markdown(erd_file_path, markdown_path)
        
        print(f"Success! Generated files in {output_dir}:")
        print(f"  - ERD file: {erd_file_path}")
        print(f"  - ER diagram: {pdf_path}")
        print(f"  - Markdown: {markdown_path}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
