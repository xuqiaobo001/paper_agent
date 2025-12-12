"""
Report Generator Module
Responsible for generating various types of reports
"""
import os
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

from .models import (
    PaperAnalysis, AggregatedKnowledge, Report
)
from .config import Config, get_config
from .llm_client import LLMHelper
from .resource_manager import ResourceManager


class ReportGenerator:
    """Report Generator"""

    @staticmethod
    def _format_table_to_markdown(table_content: str) -> str:
        """
        Convert table content string (Python list representation) to Markdown table

        Args:
            table_content: String representation of table data, e.g., "[['h1', 'h2'], ['r1c1', 'r1c2']]"

        Returns:
            Markdown formatted table string
        """
        try:
            # Try to parse as Python literal
            import ast
            table_data = ast.literal_eval(table_content)

            if not isinstance(table_data, list) or not table_data:
                return f"```\n{table_content}\n```"

            # Convert to markdown table
            markdown_lines = []

            # Header row
            if len(table_data) > 0 and isinstance(table_data[0], list):
                header = table_data[0]
                # Clean and format header cells
                header_cells = [str(cell).replace('\n', ' ').strip() for cell in header]
                markdown_lines.append('| ' + ' | '.join(header_cells) + ' |')
                markdown_lines.append('| ' + ' | '.join(['---'] * len(header_cells)) + ' |')

                # Data rows
                for row in table_data[1:]:
                    if isinstance(row, list):
                        row_cells = [str(cell).replace('\n', ' ').strip() for cell in row]
                        # Pad row to match header length
                        while len(row_cells) < len(header_cells):
                            row_cells.append('')
                        markdown_lines.append('| ' + ' | '.join(row_cells[:len(header_cells)]) + ' |')

            return '\n'.join(markdown_lines) if markdown_lines else f"```\n{table_content}\n```"

        except (ValueError, SyntaxError):
            # If parsing fails, return as code block
            return f"```\n{table_content}\n```"

    # Template text mapping for different languages
    TEMPLATES = {
        "english": {
            "authors": "Authors",
            "keywords": "Keywords",
            "summary": "Summary",
            "research_background": "Research Background",
            "research_field": "Research Field",
            "problem": "Problem",
            "motivation": "Motivation",
            "existing_limitations": "Existing Limitations",
            "technical_method": "Technical Method",
            "method_overview": "Method Overview",
            "innovations": "Innovations",
            "key_designs": "Key Designs",
            "architecture": "Architecture",
            "experiments": "Experiments",
            "datasets": "Datasets",
            "metrics": "Metrics",
            "baselines": "Baselines",
            "setup": "Setup",
            "ablation_studies": "Ablation Studies",
            "results": "Results",
            "main_results": "Main Results",
            "performance_improvements": "Performance Improvements",
            "key_findings": "Key Findings",
            "limitations": "Limitations",
            "future_work": "Future Work",
            "papers_analyzed": "Papers Analyzed",
            "overall_summary": "Overall Summary",
            "comparison_matrix": "Comparison Matrix",
            "paper": "Paper",
            "description": "Description",
            "common_themes": "Common Themes",
            "key_differences": "Key Differences",
            "individual_paper_summaries": "Individual Paper Summaries",
            "technology_timeline": "Technology Timeline",
            "identified_trends": "Identified Trends",
            "evidence": "Evidence",
        },
        "chinese": {
            "authors": "作者",
            "keywords": "关键词",
            "summary": "摘要",
            "research_background": "研究背景",
            "research_field": "研究领域",
            "problem": "问题定义",
            "motivation": "研究动机",
            "existing_limitations": "现有方法的局限性",
            "technical_method": "技术方法",
            "method_overview": "方法概述",
            "innovations": "创新点",
            "key_designs": "关键设计",
            "architecture": "架构",
            "experiments": "实验",
            "datasets": "数据集",
            "metrics": "评估指标",
            "baselines": "基线方法",
            "setup": "实验设置",
            "ablation_studies": "消融实验",
            "results": "结果",
            "main_results": "主要结果",
            "performance_improvements": "性能提升",
            "key_findings": "主要发现",
            "limitations": "局限性",
            "future_work": "未来工作",
            "papers_analyzed": "分析的论文",
            "overall_summary": "总体概述",
            "comparison_matrix": "对比矩阵",
            "paper": "论文",
            "description": "描述",
            "common_themes": "共同主题",
            "key_differences": "关键差异",
            "individual_paper_summaries": "各论文摘要",
            "technology_timeline": "技术时间线",
            "identified_trends": "识别的趋势",
            "evidence": "证据",
        }
    }

    def __init__(self, config: Optional[Config] = None):
        self.config = config or get_config()
        self.report_config = self.config.report_generator
        self.llm_helper = LLMHelper(self.config)

        # Determine language and get corresponding templates
        self.language = self.report_config.language.lower()
        if self.language not in ["chinese", "english"]:
            self.language = "english"
        self.t = self.TEMPLATES[self.language]

    def generate(
        self,
        report_type: str,
        papers: List[PaperAnalysis],
        knowledge: Optional[AggregatedKnowledge] = None,
        title: Optional[str] = None
    ) -> Report:
        """Generate report"""
        if report_type == "single":
            if not papers:
                raise ValueError("At least one paper is required")
            return self._generate_single_report(papers[0], title)

        elif report_type == "comparison":
            if len(papers) < 2:
                raise ValueError("At least two papers are required for comparison report")
            return self._generate_comparison_report(papers, knowledge, title)

        elif report_type == "trend":
            if not papers:
                raise ValueError("At least one paper is required")
            return self._generate_trend_report(papers, knowledge, title)

        else:
            raise ValueError(f"Unknown report type: {report_type}")

    def _generate_single_report(self, paper: PaperAnalysis, title: Optional[str] = None) -> Report:
        """Generate single paper reading notes"""
        report_title = title or f"Reading Notes: {paper.title}"
        content = self._render_single_template(paper)

        return Report(
            report_type="single",
            title=report_title,
            content=content,
            papers=[paper.title],
        )

    def _generate_comparison_report(
        self,
        papers: List[PaperAnalysis],
        knowledge: Optional[AggregatedKnowledge],
        title: Optional[str] = None
    ) -> Report:
        """Generate comparison report for multiple papers"""
        report_title = title or f"Paper Comparison Analysis ({len(papers)} papers)"
        content = self._render_comparison_template(papers, knowledge)

        return Report(
            report_type="comparison",
            title=report_title,
            content=content,
            papers=[p.title for p in papers],
        )

    def _generate_trend_report(
        self,
        papers: List[PaperAnalysis],
        knowledge: Optional[AggregatedKnowledge],
        title: Optional[str] = None
    ) -> Report:
        """Generate technology trend analysis report"""
        report_title = title or f"Technology Trend Analysis ({len(papers)} papers)"
        content = self._render_trend_template(papers, knowledge)

        return Report(
            report_type="trend",
            title=report_title,
            content=content,
            papers=[p.title for p in papers],
        )

    def _render_single_template(self, paper: PaperAnalysis) -> str:
        """Render single paper template"""
        sections = []
        t = self.t  # Template text

        # Title and basic info
        sections.append(f"# {paper.title}\n")

        if paper.authors:
            sections.append(f"**{t['authors']}:** {', '.join(paper.authors)}\n")

        if paper.keywords:
            sections.append(f"**{t['keywords']}:** {', '.join(paper.keywords)}\n")

        sections.append("")

        # Summary
        sections.append(f"## {t['summary']}\n")
        sections.append(paper.summary or paper.paper.abstract)
        sections.append("")

        # Research Background
        if paper.background:
            sections.append(f"## {t['research_background']}\n")
            if paper.background.research_field:
                sections.append(f"**{t['research_field']}:** {paper.background.research_field}\n")
            if paper.background.problem_definition:
                sections.append(f"**{t['problem']}:** {paper.background.problem_definition}\n")
            if paper.background.motivation:
                sections.append(f"**{t['motivation']}:** {paper.background.motivation}\n")
            if paper.background.existing_limitations:
                sections.append(f"**{t['existing_limitations']}:** {paper.background.existing_limitations}\n")
            sections.append("")

        # Technical Method
        if paper.technology:
            sections.append(f"## {t['technical_method']}\n")

            # Model type and application scenarios (prominent display)
            if hasattr(paper.technology, 'model_type') and paper.technology.model_type:
                sections.append(f"**Model Type:** {paper.technology.model_type}\n")
            if hasattr(paper.technology, 'application_scenarios') and paper.technology.application_scenarios:
                sections.append(f"**Application Scenarios:** {', '.join(paper.technology.application_scenarios)}\n")
            if paper.technology.model_type or (hasattr(paper.technology, 'application_scenarios') and paper.technology.application_scenarios):
                sections.append("")

            if paper.technology.method_overview:
                sections.append(f"**{t['method_overview']}:** {paper.technology.method_overview}\n")
            if paper.technology.innovations:
                sections.append(f"**{t['innovations']}:**")
                for i, inn in enumerate(paper.technology.innovations, 1):
                    sections.append(f"  {i}. {inn}")
                sections.append("")
            if paper.technology.key_designs:
                sections.append(f"**{t['key_designs']}:**")
                for i, design in enumerate(paper.technology.key_designs, 1):
                    sections.append(f"  {i}. {design}")
                sections.append("")
            if paper.technology.architecture:
                sections.append(f"**{t['architecture']}:** {paper.technology.architecture}\n")
            sections.append("")

        # Experimental Analysis
        if paper.experiment:
            sections.append(f"## {t['experiments']}\n")
            if paper.experiment.datasets:
                sections.append(f"**{t['datasets']}:** {', '.join(paper.experiment.datasets)}\n")
            if paper.experiment.metrics:
                sections.append(f"**{t['metrics']}:** {', '.join(paper.experiment.metrics)}\n")
            if paper.experiment.baselines:
                sections.append(f"**{t['baselines']}:** {', '.join(paper.experiment.baselines)}\n")
            if paper.experiment.setup:
                sections.append(f"**{t['setup']}:** {paper.experiment.setup}\n")
            if paper.experiment.ablation_studies:
                sections.append(f"**{t['ablation_studies']}:** {paper.experiment.ablation_studies}\n")
            sections.append("")

        # Results
        if paper.result:
            sections.append(f"## {t['results']}\n")
            if paper.result.main_results:
                sections.append(f"**{t['main_results']}:** {paper.result.main_results}\n")
            if paper.result.performance_improvements:
                sections.append(f"**{t['performance_improvements']}:** {paper.result.performance_improvements}\n")
            if paper.result.key_findings:
                sections.append(f"**{t['key_findings']}:**")
                for i, finding in enumerate(paper.result.key_findings, 1):
                    sections.append(f"  {i}. {finding}")
                sections.append("")
            if paper.result.limitations:
                sections.append(f"**{t['limitations']}:** {paper.result.limitations}\n")
            if paper.result.future_work:
                sections.append(f"**{t['future_work']}:** {paper.result.future_work}\n")
            sections.append("")

        return "\n".join(sections)

    def _render_comparison_template(
        self,
        papers: List[PaperAnalysis],
        knowledge: Optional[AggregatedKnowledge]
    ) -> str:
        """Render comparison template"""
        sections = []
        t = self.t  # Template text

        # Title
        title_text = "论文对比分析" if self.language == "chinese" else "Paper Comparison Analysis"
        sections.append(f"# {title_text}\n")

        # Paper list
        sections.append(f"## {t['papers_analyzed']}\n")
        for i, paper in enumerate(papers, 1):
            sections.append(f"{i}. **{paper.title}**")
            if paper.authors:
                author_label = "作者" if self.language == "chinese" else "Authors"
                sections.append(f"   - {author_label}: {', '.join(paper.authors)}")
        sections.append("")

        # Overall summary
        if knowledge and knowledge.overall_summary:
            sections.append(f"## {t['overall_summary']}\n")
            sections.append(knowledge.overall_summary)
            sections.append("")

        # Comparison matrix
        if knowledge and knowledge.comparison_matrix:
            sections.append(f"## {t['comparison_matrix']}\n")
            for item in knowledge.comparison_matrix:
                sections.append(f"### {item.dimension}\n")
                sections.append(f"| {t['paper']} | {t['description']} |")
                sections.append("|-------|-------------|")
                for paper_title, value in item.papers.items():
                    sections.append(f"| {paper_title} | {value} |")
                sections.append("")

        # Common themes and differences
        if knowledge:
            if knowledge.common_themes:
                sections.append(f"## {t['common_themes']}\n")
                for theme in knowledge.common_themes:
                    sections.append(f"- {theme}")
                sections.append("")

            if knowledge.key_differences:
                sections.append(f"## {t['key_differences']}\n")
                for diff in knowledge.key_differences:
                    sections.append(f"- {diff}")
                sections.append("")

        # Individual paper summaries
        sections.append(f"## {t['individual_paper_summaries']}\n")
        for paper in papers:
            sections.append(f"### {paper.title}\n")

            # Display model type and application scenarios prominently
            if paper.technology:
                if hasattr(paper.technology, 'model_type') and paper.technology.model_type:
                    sections.append(f"**Model Type:** {paper.technology.model_type}  ")
                if hasattr(paper.technology, 'application_scenarios') and paper.technology.application_scenarios:
                    sections.append(f"**Application Scenarios:** {', '.join(paper.technology.application_scenarios)}  ")
                if paper.technology.model_type or (hasattr(paper.technology, 'application_scenarios') and paper.technology.application_scenarios):
                    sections.append("")

            sections.append(paper.summary or paper.paper.abstract[:500] + "...")
            sections.append("")

        return "\n".join(sections)

    def _render_trend_template(
        self,
        papers: List[PaperAnalysis],
        knowledge: Optional[AggregatedKnowledge]
    ) -> str:
        """Render trend analysis template"""
        sections = []
        t = self.t  # Template text

        # Title
        title_text = "技术趋势分析" if self.language == "chinese" else "Technology Trend Analysis"
        sections.append(f"# {title_text}\n")

        # Paper list
        sections.append(f"## {t['papers_analyzed']}\n")
        for i, paper in enumerate(papers, 1):
            sections.append(f"{i}. {paper.title}")
        sections.append("")

        # Overall summary
        if knowledge and knowledge.overall_summary:
            sections.append(f"## {t['overall_summary']}\n")
            sections.append(knowledge.overall_summary)
            sections.append("")

        # Timeline
        if knowledge and knowledge.timeline:
            sections.append(f"## {t['technology_timeline']}\n")
            for item in knowledge.timeline:
                date_str = f"({item.date})" if item.date else ""
                sections.append(f"**{item.order}. {item.paper_title}** {date_str}")
                sections.append(f"   - {item.key_contribution}")
                sections.append("")

        # Trends
        if knowledge and knowledge.trends:
            sections.append(f"## {t['identified_trends']}\n")
            for trend in knowledge.trends:
                sections.append(f"### {trend.trend_name}\n")
                sections.append(f"{trend.description}\n")
                if trend.evidence:
                    sections.append(f"**{t['evidence']}:**")
                    for ev in trend.evidence:
                        sections.append(f"- {ev}")
                sections.append("")

        # Common themes
        if knowledge and knowledge.common_themes:
            sections.append(f"## {t['common_themes']}\n")
            for theme in knowledge.common_themes:
                sections.append(f"- {theme}")
            sections.append("")

        # Key differences
        if knowledge and knowledge.key_differences:
            sections.append(f"## {t['key_differences']}\n")
            for diff in knowledge.key_differences:
                sections.append(f"- {diff}")
            sections.append("")

        return "\n".join(sections)

    def save_report(self, report: Report, output_path: str, papers: Optional[List[PaperAnalysis]] = None) -> str:
        """Save report to file and extract resources

        Args:
            report: Report object to save
            output_path: Path to save the report
            papers: List of paper analyses (needed to save resources)

        Returns:
            Path to saved report
        """
        # Determine format
        output_format = self.report_config.output_format.lower()

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        # Save resources if papers provided and format is markdown
        if papers and output_format == "markdown":
            resource_mgr = ResourceManager(output_path)
            # Extract PaperContent from PaperAnalysis
            paper_contents = [p.paper for p in papers]
            resources = resource_mgr.save_resources(paper_contents)

            # Add resource references to report content
            report.content = self._add_resource_references(report.content, papers, resources, resource_mgr)

        if output_format == "json":
            content = json.dumps({
                "report_type": report.report_type,
                "title": report.title,
                "content": report.content,
                "generated_at": report.generated_at.isoformat(),
                "papers": report.papers,
                "metadata": report.metadata,
            }, ensure_ascii=False, indent=2)

        elif output_format == "html":
            content = self._convert_to_html(report)

        else:  # markdown
            content = report.content

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return output_path

    def _convert_to_html(self, report: Report) -> str:
        """Convert report to HTML format"""
        try:
            import markdown
            html_content = markdown.markdown(report.content, extensions=['tables', 'fenced_code'])
        except ImportError:
            # Simple fallback conversion
            html_content = f"<pre>{report.content}</pre>"

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{report.title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; line-height: 1.6; }}
        h1 {{ color: #333; border-bottom: 2px solid #333; padding-bottom: 10px; }}
        h2 {{ color: #444; margin-top: 30px; }}
        h3 {{ color: #555; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f5f5f5; }}
        code {{ background-color: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
        pre {{ background-color: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        blockquote {{ border-left: 4px solid #ddd; margin: 0; padding-left: 20px; color: #666; }}
    </style>
</head>
<body>
{html_content}
<footer>
    <p><small>Generated at: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}</small></p>
</footer>
</body>
</html>"""

        return html

    def _add_resource_references(self, content: str, papers: List[PaperAnalysis],
                                   resources: Dict[str, Dict], resource_mgr: ResourceManager) -> str:
        """
        Add references to key figures, tables, and equations in the report

        Args:
            content: Original report content
            papers: List of paper analyses with key resource indices
            resources: Saved resources dictionary
            resource_mgr: Resource manager instance

        Returns:
            Modified report content with resource references
        """
        # Add a resources section at the end
        resources_section = "\n\n---\n\n## Key Resources\n\n"

        for paper in papers:
            paper_res = resources.get(paper.title, {})

            if not (paper.key_figures or paper.key_tables or paper.key_equations):
                continue

            resources_section += f"### {paper.title}\n\n"

            # Add key figures
            if paper.key_figures and paper_res.get('figures'):
                resources_section += "#### Key Figures\n\n"
                for fig_idx in paper.key_figures:
                    # Find the corresponding saved figure
                    for fig_info in paper_res['figures']:
                        if fig_info['index'] == fig_idx:
                            resources_section += f"**{fig_info['caption']}**\n\n"
                            resources_section += f"![{fig_info['caption']}]({fig_info['path']})\n\n"
                            break

            # Add key tables
            if paper.key_tables and paper_res.get('tables'):
                resources_section += "#### Key Tables\n\n"
                for table_idx in paper.key_tables:
                    for table_info in paper_res['tables']:
                        if table_info['index'] == table_idx:
                            caption = table_info.get('caption', f"Table {table_idx}")
                            resources_section += f"**{caption}**\n\n"

                            # Check if table is saved as image
                            if table_info.get('is_image', False):
                                # Display as image
                                resources_section += f"![{caption}]({table_info['path']})\n\n"
                            else:
                                # Format table as Markdown
                                table_content = table_info['content']
                                formatted_table = self._format_table_to_markdown(table_content)
                                resources_section += f"{formatted_table}\n\n"
                            break

            # Add key equations
            if paper.key_equations and paper_res.get('equations'):
                resources_section += "#### Key Equations\n\n"
                for eq_idx in paper.key_equations:
                    for eq_info in paper_res['equations']:
                        if eq_info['index'] == eq_idx:
                            resources_section += f"{eq_info['latex']}\n\n"
                            break

        return content + resources_section


def generate_report(
    report_type: str,
    papers: List[PaperAnalysis],
    knowledge: Optional[AggregatedKnowledge] = None,
    title: Optional[str] = None,
    config: Optional[Config] = None
) -> Report:
    """Convenience function: Generate report"""
    generator = ReportGenerator(config)
    return generator.generate(report_type, papers, knowledge, title)


def save_report(
    report: Report,
    output_path: str,
    papers: Optional[List[PaperAnalysis]] = None,
    config: Optional[Config] = None
) -> str:
    """Convenience function: Save report to file"""
    generator = ReportGenerator(config)
    return generator.save_report(report, output_path, papers)
