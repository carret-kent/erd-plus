#!/usr/bin/env python3
"""
ERD Generator
Converts MySQL schema data to Haskell ERD format and generates diagrams
"""

import subprocess
from pathlib import Path
from typing import Dict, Any, List

class ERDGenerator:
    def __init__(self, schema_data: Dict[str, Any]):
        """Initialize with schema data"""
        self.schema_data = schema_data
    
    def _get_column_cardinality(self, column: Dict[str, Any]) -> str:
        """Determine ERD cardinality symbol for a column"""
        if column['COLUMN_KEY'] == 'PRI':
            return '*'  # Primary key
        elif column['IS_NULLABLE'] == 'NO':
            return '+'  # Required field (1 or more)
        else:
            return ''   # Optional field (0 or more)
    
    def _format_column_name(self, column: Dict[str, Any]) -> str:
        """Format column name with cardinality symbol and label attribute"""
        cardinality = self._get_column_cardinality(column)
        column_name = f"{cardinality}{column['COLUMN_NAME']}"
        
        # Generate label attribute with detailed information
        label_parts = []
        
        # Data type with length/precision
        data_type = column['DATA_TYPE']
        if column['CHARACTER_MAXIMUM_LENGTH']:
            data_type += f"({column['CHARACTER_MAXIMUM_LENGTH']})"
        elif column['NUMERIC_PRECISION'] and column['NUMERIC_SCALE']:
            data_type += f"({column['NUMERIC_PRECISION']},{column['NUMERIC_SCALE']})"
        elif column['NUMERIC_PRECISION']:
            data_type += f"({column['NUMERIC_PRECISION']})"
        
        label_parts.append(data_type)
        
        # Constraints
        if column['EXTRA'] and 'auto_increment' in column['EXTRA'].lower():
            label_parts.append('auto_increment')
        
        if column['COLUMN_KEY'] == 'PRI':
            label_parts.append('primary key')
        elif column['COLUMN_KEY'] == 'UNI':
            label_parts.append('unique')
        elif column['COLUMN_KEY'] == 'MUL':
            label_parts.append('foreign key')
        
        if column['IS_NULLABLE'] == 'NO':
            label_parts.append('not null')
        
        if column['COLUMN_DEFAULT'] is not None:
            default_value = column['COLUMN_DEFAULT']
            if default_value == 'CURRENT_TIMESTAMP':
                label_parts.append('default current_timestamp')
            else:
                label_parts.append(f"default {default_value}")
        
        # Add Japanese comment if exists
        if column['COLUMN_COMMENT'] and column['COLUMN_COMMENT'].strip():
            label_parts.append(column['COLUMN_COMMENT'].strip())
        
        # Format with label attribute
        if label_parts:
            label_content = ', '.join(label_parts)
            return f'{column_name} {{label: "{label_content}"}}'
        else:
            return column_name
    
    def _generate_table_definition(self, table_name: str, table_data: Dict[str, Any]) -> str:
        """Generate ERD table definition"""
        lines = [f"[{table_name}]"]
        
        for column in table_data['columns']:
            formatted_column = self._format_column_name(column)
            lines.append(formatted_column)
        
        return '\n'.join(lines)
    
    def _generate_relationships(self) -> List[str]:
        """Generate ERD relationship definitions"""
        relationships = []
        
        for fk in self.schema_data['relationships']:
            source_table = fk['TABLE_NAME']
            target_table = fk['REFERENCED_TABLE_NAME']
            
            # Default relationship: many-to-one (foreign key side is many, referenced side is one)
            relationship = f"{source_table} *--1 {target_table}"
            relationships.append(relationship)
        
        return relationships
    
    def generate_erd_file(self, output_path: Path) -> None:
        """Generate .er file from schema data"""
        erd_content = []
        
        # Add header comment
        erd_content.append("# Generated ERD file from MySQL schema")
        erd_content.append(f"# Database: {self.schema_data['database']}")
        if 'schema' in self.schema_data:
            erd_content.append(f"# Schema: {self.schema_data['schema']}")
        erd_content.append("")
        
        # Generate table definitions
        for table_name, table_data in self.schema_data['tables'].items():
            table_def = self._generate_table_definition(table_name, table_data)
            erd_content.append(table_def)
            erd_content.append("")  # Empty line between tables
        
        # Generate relationships
        relationships = self._generate_relationships()
        if relationships:
            erd_content.append("# Relationships")
            erd_content.extend(relationships)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(erd_content))
        
        print(f"ERD file generated: {output_path}")
    
    def generate_diagram(self, erd_file_path: Path, output_image_path: Path) -> None:
        """Generate ER diagram using Haskell ERD tool or fallback to Graphviz"""
        print(f"Debug: generate_diagram called with output_image_path = {output_image_path}")
        try:
            # Try Haskell ERD first
            print("Debug: Attempting Haskell ERD...")
            self._generate_with_haskell_erd(erd_file_path, output_image_path)
        except Exception as e:
            print(f"Haskell ERD not available ({e}), using Graphviz fallback...")
            print(f"Debug: Switching to Graphviz with path = {output_image_path}")
            self._generate_with_graphviz(output_image_path)
    
    def _generate_with_haskell_erd(self, erd_file_path: Path, output_image_path: Path) -> None:
        """Generate ER diagram using Haskell ERD tool"""
        # Run erd command to generate PDF
        cmd = [
            'erd',
            '-i', str(erd_file_path),
            '-o', str(output_image_path),
            '-f', 'pdf'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"ER diagram generated with Haskell ERD: {output_image_path}")
    
    def _generate_with_graphviz(self, output_image_path: Path) -> None:
        """Generate ER diagram using Graphviz as fallback"""
        from graphviz_erd import GraphvizERDGenerator
        
        graphviz_generator = GraphvizERDGenerator(self.schema_data)
        graphviz_generator.generate_diagram(output_image_path)
