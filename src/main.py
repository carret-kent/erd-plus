#!/usr/bin/env python3
"""
ERD Plus - MySQL Schema to ERD Generator
Main entry point for the application
"""

import os
import sys
import json
from pathlib import Path
from db_connector import MySQLSchemaExtractor
from erd_generator import ERDGenerator
from markdown_converter import MarkdownConverter
from test_simple import test_mysql_connection

def load_config(config_path="/data/definition.json"):
    """Load database configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file {config_path} not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {config_path}")
        sys.exit(1)

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
