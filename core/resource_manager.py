"""
Resource Manager Module
Responsible for saving figures, tables, and equations as assets
"""
import os
import base64
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from .models import PaperContent, Figure, Table, Equation


class ResourceManager:
    """Manage resources (figures, tables, equations) for reports"""

    def __init__(self, output_path: str):
        """
        Initialize resource manager

        Args:
            output_path: Path to the output report file
        """
        self.output_path = output_path
        self.output_dir = os.path.dirname(output_path) or "."
        self.report_name = Path(output_path).stem

        # Create assets directory
        self.assets_dir = os.path.join(self.output_dir, f"{self.report_name}_assets")
        os.makedirs(self.assets_dir, exist_ok=True)

        # Track saved resources
        self.saved_figures: Dict[str, str] = {}  # figure_id -> relative_path
        self.saved_tables: Dict[str, str] = {}   # table_id -> relative_path
        self.saved_equations: Dict[str, str] = {}  # equation_id -> latex_text

    def save_figure(self, figure: Figure, paper_title: str, fig_index: int) -> Optional[str]:
        """
        Save figure image to assets directory

        Args:
            figure: Figure object with image data
            paper_title: Paper title (used for naming)
            fig_index: Figure index in the paper

        Returns:
            Relative path to saved image, or None if no image data
        """
        if not figure.image_data:
            return None

        # Generate safe filename
        safe_title = self._sanitize_filename(paper_title)
        filename = f"fig_{safe_title}_{fig_index}.png"
        filepath = os.path.join(self.assets_dir, filename)

        # Save image
        try:
            with open(filepath, 'wb') as f:
                f.write(figure.image_data)

            # Generate relative path for markdown
            relative_path = os.path.join(f"{self.report_name}_assets", filename)

            # Store mapping
            figure_id = f"{safe_title}_fig_{fig_index}"
            self.saved_figures[figure_id] = relative_path

            return relative_path

        except Exception as e:
            print(f"Failed to save figure {filename}: {e}")
            return None

    def save_table(self, table: Table, paper_title: str, table_index: int) -> str:
        """
        Save table to file in assets directory.
        If table has image_data, save as PNG. Otherwise save as markdown.

        Args:
            table: Table object
            paper_title: Paper title
            table_index: Table index

        Returns:
            Relative path to saved table file
        """
        safe_title = self._sanitize_filename(paper_title)

        # If table has image data (screenshot), save as PNG
        if table.image_data:
            filename = f"table_{safe_title}_{table_index}.png"
            filepath = os.path.join(self.assets_dir, filename)

            try:
                with open(filepath, 'wb') as f:
                    f.write(table.image_data)

                relative_path = os.path.join(f"{self.report_name}_assets", filename)
                table_id = f"{safe_title}_table_{table_index}"
                self.saved_tables[table_id] = relative_path

                return relative_path

            except Exception as e:
                print(f"Failed to save table image {filename}: {e}")
                return ""

        # Otherwise save as markdown
        filename = f"table_{safe_title}_{table_index}.md"
        filepath = os.path.join(self.assets_dir, filename)

        # Format table content
        table_content = f"## Table {table_index}\n\n"
        if table.caption:
            table_content += f"**Caption:** {table.caption}\n\n"
        table_content += f"```\n{table.content}\n```\n"

        # Save to file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(table_content)

            relative_path = os.path.join(f"{self.report_name}_assets", filename)
            table_id = f"{safe_title}_table_{table_index}"
            self.saved_tables[table_id] = relative_path

            return relative_path

        except Exception as e:
            print(f"Failed to save table {filename}: {e}")
            return ""

    def format_equation(self, equation: Equation) -> str:
        """
        Format equation for markdown display

        Args:
            equation: Equation object

        Returns:
            Formatted LaTeX equation string for markdown
        """
        # Check if it's already in LaTeX format
        if '\\' in equation.equation_text or equation.equation_text.strip().startswith('$'):
            latex = equation.equation_text.strip()
        else:
            # Wrap in LaTeX delimiters
            latex = f"$${equation.equation_text}$$"

        # Add equation number if present
        if equation.equation_number:
            latex = f"{latex} &nbsp;&nbsp;&nbsp;&nbsp; {equation.equation_number}"

        return latex

    def save_resources(self, papers: List[PaperContent]) -> Dict[str, Dict]:
        """
        Save all resources from papers

        Args:
            papers: List of paper contents

        Returns:
            Dictionary mapping paper titles to their saved resources
        """
        resources = {}

        for paper in papers:
            paper_resources = {
                'figures': [],
                'tables': [],
                'equations': []
            }

            # Save figures
            for idx, figure in enumerate(paper.figures, 1):
                rel_path = self.save_figure(figure, paper.title, idx)
                if rel_path:
                    paper_resources['figures'].append({
                        'index': idx,
                        'path': rel_path,
                        'caption': figure.caption,
                        'page': figure.page
                    })

            # Save tables
            for idx, table in enumerate(paper.tables, 1):
                rel_path = self.save_table(table, paper.title, idx)
                if rel_path:
                    paper_resources['tables'].append({
                        'index': idx,
                        'path': rel_path,
                        'caption': table.caption,
                        'content': table.content,
                        'page': table.page,
                        'is_image': table.image_data is not None  # Flag to indicate if it's an image
                    })

            # Format equations
            for idx, equation in enumerate(paper.equations, 1):
                formatted = self.format_equation(equation)
                paper_resources['equations'].append({
                    'index': idx,
                    'latex': formatted,
                    'number': equation.equation_number,
                    'page': equation.page
                })

            resources[paper.title] = paper_resources

        return resources

    def _sanitize_filename(self, name: str) -> str:
        """
        Sanitize string to be safe for filename

        Args:
            name: Original name

        Returns:
            Sanitized filename-safe string
        """
        # Remove or replace unsafe characters
        safe = name.lower()
        safe = safe.replace(' ', '_')
        safe = ''.join(c for c in safe if c.isalnum() or c in ('_', '-'))
        # Limit length
        return safe[:50]

    def generate_resource_summary(self, resources: Dict[str, Dict]) -> str:
        """
        Generate a markdown summary of saved resources

        Args:
            resources: Resources dictionary from save_resources()

        Returns:
            Markdown formatted summary
        """
        summary = "## Extracted Resources\n\n"

        for paper_title, paper_res in resources.items():
            summary += f"### {paper_title}\n\n"

            if paper_res['figures']:
                summary += f"**Figures:** {len(paper_res['figures'])} extracted\n"
            if paper_res['tables']:
                summary += f"**Tables:** {len(paper_res['tables'])} extracted\n"
            if paper_res['equations']:
                summary += f"**Equations:** {len(paper_res['equations'])} extracted\n"

            summary += "\n"

        return summary


def create_resource_manager(output_path: str) -> ResourceManager:
    """Convenience function: Create resource manager"""
    return ResourceManager(output_path)
