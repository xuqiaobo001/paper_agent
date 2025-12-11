"""
Paper Agent Main Class
Provides one-click execution of the complete analysis workflow
"""
import os
import glob as glob_module
from pathlib import Path
from typing import Optional, List, Union

from .core.config import Config, get_config
from .core.models import PaperContent, PaperAnalysis, AggregatedKnowledge, Report
from .core.pdf_parser import PDFParser
from .core.content_extractor import ContentExtractor
from .core.knowledge_aggregator import KnowledgeAggregator
from .core.report_generator import ReportGenerator


class PaperAgent:
    """Paper Reading Agent"""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize Paper Agent

        Args:
            config_path: Path to configuration file, auto-detect if not provided
        """
        self.config = Config(config_path) if config_path else get_config()

        # Initialize modules
        self.pdf_parser = PDFParser(self.config)
        self.content_extractor = ContentExtractor(self.config)
        self.knowledge_aggregator = KnowledgeAggregator(self.config)
        self.report_generator = ReportGenerator(self.config)

        # Cache data
        self._papers: List[PaperContent] = []
        self._analyses: List[PaperAnalysis] = []
        self._knowledge: Optional[AggregatedKnowledge] = None

    def load_papers(self, input_path: Union[str, List[str]]) -> List[PaperContent]:
        """Load papers

        Args:
            input_path: Can be:
                - Single PDF file path
                - Directory path (loads all PDFs)
                - List of PDF file paths
                - Glob pattern (e.g., "papers/*.pdf")

        Returns:
            List of loaded paper content
        """
        pdf_paths = self._resolve_paths(input_path)

        if not pdf_paths:
            raise ValueError(f"No PDF files found: {input_path}")

        print(f"Loading {len(pdf_paths)} PDF files...")
        self._papers = self.pdf_parser.parse_all(pdf_paths)
        print(f"Successfully loaded {len(self._papers)} papers")

        return self._papers

    def analyze(self, papers: Optional[List[PaperContent]] = None) -> List[PaperAnalysis]:
        """Analyze paper content

        Args:
            papers: List of papers to analyze, uses loaded papers if not provided

        Returns:
            List of analysis results
        """
        papers = papers or self._papers
        if not papers:
            raise ValueError("No papers to analyze")

        print(f"Analyzing {len(papers)} papers...")
        self._analyses = []

        for i, paper in enumerate(papers, 1):
            print(f"  [{i}/{len(papers)}] Analyzing: {paper.title[:50]}...")
            try:
                analysis = self.content_extractor.extract(paper)
                self._analyses.append(analysis)
            except Exception as e:
                print(f"    Failed: {e}")

        print(f"Successfully analyzed {len(self._analyses)} papers")
        return self._analyses

    def aggregate(self, analyses: Optional[List[PaperAnalysis]] = None, custom_prompt: Optional[str] = None) -> AggregatedKnowledge:
        """Aggregate knowledge from multiple papers

        Args:
            analyses: List of analysis results, uses cache if not provided
            custom_prompt: Custom analysis requirement

        Returns:
            Aggregated knowledge
        """
        analyses = analyses or self._analyses
        if not analyses:
            raise ValueError("No analysis results to aggregate")

        print(f"Aggregating knowledge from {len(analyses)} papers...")
        self._knowledge = self.knowledge_aggregator.aggregate(analyses, custom_prompt=custom_prompt)
        print("Knowledge aggregation complete")

        return self._knowledge

    def generate_report(
        self,
        report_type: str = "single",
        title: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> Report:
        """Generate analysis report

        Args:
            report_type: Report type (single/comparison/trend)
            title: Report title
            output_path: Output path

        Returns:
            Generated report
        """
        if not self._analyses:
            raise ValueError("No analysis results available, please run analyze first")

        # Ensure knowledge is aggregated (needed for comparison and trend reports)
        if report_type in ["comparison", "trend"] and self._knowledge is None:
            self.aggregate()

        print(f"Generating {report_type} report...")
        report = self.report_generator.generate(
            report_type=report_type,
            papers=self._analyses,
            knowledge=self._knowledge,
            title=title,
        )

        if output_path:
            self.report_generator.save_report(report, output_path, self._analyses)
            print(f"Report saved to: {output_path}")

        return report

    def run(
        self,
        input_path: Union[str, List[str]],
        report_type: str = "single",
        output_path: Optional[str] = None,
        title: Optional[str] = None,
        custom_prompt: Optional[str] = None
    ) -> Report:
        """One-click execution of complete workflow

        Args:
            input_path: Input path (PDF file, directory, or list)
            report_type: Report type (single/comparison/trend)
            output_path: Output path
            title: Report title
            custom_prompt: Custom analysis requirement

        Returns:
            Generated report
        """
        # Load papers
        self.load_papers(input_path)

        # Analyze
        self.analyze()

        # Aggregate (for comparison and trend reports)
        if report_type in ["comparison", "trend"] or len(self._analyses) > 1:
            self.aggregate(custom_prompt=custom_prompt)

        # Generate report
        return self.generate_report(report_type, title, output_path)

    def _resolve_paths(self, input_path: Union[str, List[str]]) -> List[str]:
        """Resolve input paths to PDF file list"""
        if isinstance(input_path, list):
            paths = []
            for p in input_path:
                paths.extend(self._resolve_single_path(p))
            return paths
        else:
            return self._resolve_single_path(input_path)

    def _resolve_single_path(self, path: str) -> List[str]:
        """Resolve single path"""
        # Check if it's a glob pattern
        if '*' in path or '?' in path:
            return sorted(glob_module.glob(path))

        path = os.path.abspath(path)

        if os.path.isfile(path):
            if path.lower().endswith('.pdf'):
                return [path]
            else:
                return []

        elif os.path.isdir(path):
            # Find all PDFs in directory
            pdfs = []
            for ext in ['*.pdf', '*.PDF']:
                pdfs.extend(glob_module.glob(os.path.join(path, ext)))
            return sorted(pdfs)

        else:
            return []

    @property
    def papers(self) -> List[PaperContent]:
        """Get loaded papers"""
        return self._papers

    @property
    def analyses(self) -> List[PaperAnalysis]:
        """Get analysis results"""
        return self._analyses

    @property
    def knowledge(self) -> Optional[AggregatedKnowledge]:
        """Get aggregated knowledge"""
        return self._knowledge

    def clear(self) -> None:
        """Clear all cached data"""
        self._papers = []
        self._analyses = []
        self._knowledge = None
