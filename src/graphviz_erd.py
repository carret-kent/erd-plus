#!/usr/bin/env python3
"""
Graphviz ERD Generator
Alternative to Haskell ERD using Python Graphviz
"""

from graphviz import Digraph
from pathlib import Path
from typing import Dict, Any, List

class GraphvizERDGenerator:
    def __init__(self, schema_data: Dict[str, Any]):
        """Initialize with schema data"""
        self.schema_data = schema_data
    
    def generate_diagram(self, output_path: Path) -> None:
        """Generate ER diagram using Graphviz"""
        dot = Digraph(comment='Database ERD')
        dot.attr(rankdir='TB', size='12,8')
        dot.attr('node', shape='plaintext')
        
        # Generate table nodes
        for table_name, table_data in self.schema_data['tables'].items():
            table_html = self._generate_table_html(table_name, table_data['columns'])
            dot.node(table_name, table_html)
        
        # Generate relationships
        for relationship in self.schema_data['relationships']:
            source_table = relationship['TABLE_NAME']
            target_table = relationship['REFERENCED_TABLE_NAME']
            label = f"{relationship['COLUMN_NAME']} -> {relationship['REFERENCED_COLUMN_NAME']}"
            
            dot.edge(source_table, target_table, label=label, 
                    arrowhead='crow', arrowtail='none')
        
        # Render to PDF
        base_path = str(output_path.with_suffix(''))
        print(f"Debug: output_path = {output_path}")
        print(f"Debug: base_path = {base_path}")
        print(f"Debug: Rendering with format='pdf'")
        
        dot.render(base_path, format='pdf', cleanup=True)
        print(f"ER diagram generated: {output_path}")
    
    def _generate_table_html(self, table_name: str, columns: List[Dict[str, Any]]) -> str:
        """Generate HTML table representation for Graphviz"""
        html = f'<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0">'
        html += f'<TR><TD BGCOLOR="lightblue"><B>{table_name}</B></TD></TR>'
        
        for column in columns:
            column_name = column['COLUMN_NAME']
            data_type = column['DATA_TYPE']
            
            # Format column with indicators
            indicators = []
            if column['COLUMN_KEY'] == 'PRI':
                indicators.append('🔑')  # Primary key
            if column['COLUMN_KEY'] == 'MUL':
                indicators.append('🔗')  # Foreign key
            if column['IS_NULLABLE'] == 'NO':
                indicators.append('*')   # Required
            
            indicator_str = ' '.join(indicators)
            display_name = f"{indicator_str} {column_name}" if indicator_str else column_name
            
            html += f'<TR><TD ALIGN="LEFT">{display_name} : {data_type}</TD></TR>'
        
        html += '</TABLE>>'
        return html
