#!/usr/bin/env python3
"""
Markdown Converter
Converts ERD files to Markdown format for LLM consumption
"""

from pathlib import Path
from typing import List, Dict, Any
import re

class MarkdownConverter:
    def __init__(self):
        """Initialize Markdown converter"""
        pass
    
    def _parse_erd_file(self, erd_file_path: Path) -> Dict[str, Any]:
        """Parse ERD file and extract tables and relationships"""
        with open(erd_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tables = {}
        relationships = []
        current_table = None
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            
            # Skip comments and empty lines
            if line.startswith('#') or not line:
                continue
            
            # Table definition
            if line.startswith('[') and line.endswith(']'):
                current_table = line[1:-1]  # Remove brackets
                tables[current_table] = []
            
            # Column definition
            elif current_table and not '--' in line:
                tables[current_table].append(line)
            
            # Relationship definition
            elif '--' in line:
                relationships.append(line)
                current_table = None
        
        return {
            'tables': tables,
            'relationships': relationships
        }
    
    def _format_table_markdown(self, table_name: str, columns: List[str]) -> str:
        """Format table as Markdown"""
        markdown = [f"## {table_name}"]
        markdown.append("")
        
        if columns:
            markdown.append("| Column | Type | Notes |")
            markdown.append("|--------|------|-------|")
            
            for column in columns:
                # Parse column with cardinality symbols
                notes = []
                clean_column = column
                
                if column.startswith('*'):
                    notes.append("Primary Key")
                    clean_column = column[1:]
                elif column.startswith('+'):
                    notes.append("Required")
                    clean_column = column[1:]
                
                markdown.append(f"| {clean_column} | - | {', '.join(notes) if notes else '-'} |")
        
        markdown.append("")
        return '\n'.join(markdown)
    
    def _format_relationships_markdown(self, relationships: List[str]) -> str:
        """Format relationships as Markdown"""
        if not relationships:
            return ""
        
        markdown = ["## Relationships", ""]
        
        for relationship in relationships:
            # Parse relationship format: Table1 *--1 Table2
            parts = relationship.split()
            if len(parts) >= 3:
                source = parts[0]
                relation_type = parts[1]
                target = parts[2]
                
                # Convert ERD notation to readable format
                cardinality_map = {
                    '*--1': "Many-to-One",
                    '1--*': "One-to-Many", 
                    '1--1': "One-to-One",
                    '*--*': "Many-to-Many"
                }
                
                readable_type = cardinality_map.get(relation_type, relation_type)
                markdown.append(f"- **{source}** → **{target}** ({readable_type})")
        
        markdown.append("")
        return '\n'.join(markdown)
    
    def convert_erd_to_markdown(self, erd_file_path: Path, output_path: Path) -> None:
        """Convert ERD file to Markdown format"""
        # Parse ERD file
        erd_data = self._parse_erd_file(erd_file_path)
        
        # Generate Markdown content
        markdown_content = []
        
        # Title
        markdown_content.append("# Database Schema")
        markdown_content.append("")
        markdown_content.append(f"Generated from: `{erd_file_path.name}`")
        markdown_content.append("")
        
        # Tables
        if erd_data['tables']:
            markdown_content.append("# Tables")
            markdown_content.append("")
            
            for table_name, columns in erd_data['tables'].items():
                table_md = self._format_table_markdown(table_name, columns)
                markdown_content.append(table_md)
        
        # Relationships
        if erd_data['relationships']:
            relationships_md = self._format_relationships_markdown(erd_data['relationships'])
            markdown_content.append(relationships_md)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(markdown_content))
        
        print(f"Markdown file generated: {output_path}")
