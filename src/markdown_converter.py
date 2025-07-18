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
    
    def _parse_column_info(self, column_text: str) -> Dict[str, str]:
        """Parse column information from ERD format"""
        column_info = {
            'name': '',
            'type': '',
            'constraints': [],
            'comment': ''
        }
        
        # Extract column name (before {label:)
        if '{label:' in column_text:
            column_info['name'] = column_text.split('{label:')[0].strip()
            
            # Extract label content
            label_match = re.search(r'\{label:\s*"([^"]+)"\}', column_text)
            if label_match:
                label_content = label_match.group(1)
                
                # Split label by comma and process each part
                parts = [part.strip() for part in label_content.split(',')]
                
                for i, part in enumerate(parts):
                    if i == 0:
                        # First part is usually the data type
                        column_info['type'] = part
                    elif any(constraint in part.lower() for constraint in 
                           ['primary key', 'foreign key', 'unique', 'not null', 'auto_increment', 'default']):
                        # Constraint keywords
                        column_info['constraints'].append(part)
                    else:
                        # Assume it's a comment (especially if it contains Japanese characters)
                        if re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', part):
                            column_info['comment'] = part
                        else:
                            column_info['constraints'].append(part)
        else:
            # Fallback: use the whole text as column name
            column_info['name'] = column_text.strip()
        
        # Remove cardinality symbols from name
        if column_info['name'].startswith('*'):
            column_info['name'] = column_info['name'][1:].strip()
            if 'primary key' not in ' '.join(column_info['constraints']).lower():
                column_info['constraints'].insert(0, 'Primary Key')
        elif column_info['name'].startswith('+'):
            column_info['name'] = column_info['name'][1:].strip()
            if 'foreign key' not in ' '.join(column_info['constraints']).lower():
                column_info['constraints'].insert(0, 'Foreign Key')
        
        return column_info
    
    def _format_table_markdown(self, table_name: str, columns: List[str]) -> str:
        """Format table as Markdown"""
        markdown = [f"## {table_name}"]
        markdown.append("")
        
        if columns:
            markdown.append("| Column | Type | Constraints | Comment |")
            markdown.append("|--------|------|-------------|---------|")
            
            for column in columns:
                col_info = self._parse_column_info(column)
                
                # Format constraints
                constraints_text = ', '.join(col_info['constraints']) if col_info['constraints'] else '-'
                
                # Format comment
                comment_text = col_info['comment'] if col_info['comment'] else '-'
                
                markdown.append(f"| {col_info['name']} | {col_info['type']} | {constraints_text} | {comment_text} |")
        
        markdown.append("")
        return '\n'.join(markdown)
    
    def _format_relationships_markdown(self, relationships: List[str]) -> str:
        """Format relationships as Markdown"""
        if not relationships:
            return ""
        
        markdown = ["# Relationships", ""]
        markdown.append("| Relationship | Type | Description |")
        markdown.append("|--------------|------|-------------|")
        
        for relationship in relationships:
            # Parse relationship format: Table1 *--1 Table2
            parts = relationship.split()
            if len(parts) >= 3:
                source = parts[0]
                relation_type = parts[1]
                target = parts[2]
                
                # Convert ERD notation to readable format
                cardinality_map = {
                    '*--1': ("Many-to-One", f"Many {source} records can relate to one {target} record"),
                    '1--*': ("One-to-Many", f"One {source} record can relate to many {target} records"), 
                    '1--1': ("One-to-One", f"One {source} record relates to one {target} record"),
                    '*--*': ("Many-to-Many", f"Many {source} records can relate to many {target} records"),
                    '0--1': ("Zero-or-One", f"{source} may optionally relate to one {target} record"),
                    '1--0': ("One-to-Zero", f"One {source} record may optionally relate to {target}"),
                    '+--1': ("One-or-More to One", f"One or more {source} records relate to one {target} record"),
                    '1--+': ("One to One-or-More", f"One {source} record relates to one or more {target} records")
                }
                
                readable_type, description = cardinality_map.get(relation_type, (relation_type, f"{source} relates to {target}"))
                relationship_display = f"{source} → {target}"
                markdown.append(f"| {relationship_display} | {readable_type} | {description} |")
        
        markdown.append("")
        return '\n'.join(markdown)
    
    def convert_erd_to_markdown(self, erd_file_path: Path, output_path: Path) -> None:
        """Convert ERD file to Markdown format"""
        # Parse ERD file
        erd_data = self._parse_erd_file(erd_file_path)
        
        # Generate Markdown content
        markdown_content = []
        
        # Title and metadata
        database_name = erd_file_path.stem
        markdown_content.append(f"# Database Schema: {database_name}")
        markdown_content.append("")
        markdown_content.append(f"**Generated from:** `{erd_file_path.name}`")
        markdown_content.append(f"**Tables:** {len(erd_data['tables'])}")
        markdown_content.append(f"**Relationships:** {len(erd_data['relationships'])}")
        markdown_content.append("")
        
        # Table of Contents
        if erd_data['tables']:
            markdown_content.append("## Table of Contents")
            markdown_content.append("")
            for table_name in sorted(erd_data['tables'].keys()):
                markdown_content.append(f"- [{table_name}](#{table_name.lower()})")
            markdown_content.append("")
        
        # Tables
        if erd_data['tables']:
            markdown_content.append("# Tables")
            markdown_content.append("")
            
            # Sort tables alphabetically for better readability
            for table_name in sorted(erd_data['tables'].keys()):
                columns = erd_data['tables'][table_name]
                table_md = self._format_table_markdown(table_name, columns)
                markdown_content.append(table_md)
        
        # Relationships
        if erd_data['relationships']:
            relationships_md = self._format_relationships_markdown(erd_data['relationships'])
            markdown_content.append(relationships_md)
        
        # Additional metadata
        markdown_content.append("---")
        markdown_content.append("")
        markdown_content.append("*Generated by ERD Plus - MySQL Schema to ERD Generation System*")
        markdown_content.append("")
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(markdown_content))
        
        print(f"Markdown file generated: {output_path}")
