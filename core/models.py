"""
Data Model Definitions
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class Figure:
    """Figure information"""
    page: int
    caption: str = ""
    image_data: Optional[bytes] = None


@dataclass
class Table:
    """Table information"""
    page: int
    caption: str = ""
    content: str = ""
    image_data: Optional[bytes] = None  # Screenshot of table when text extraction fails


@dataclass
class Equation:
    """Equation information"""
    page: int
    equation_text: str  # LaTeX or plain text format
    equation_number: Optional[str] = None  # e.g., "(1)", "Eq. 1"
    caption: str = ""  # Description of the equation


@dataclass
class Reference:
    """Reference information"""
    index: int
    text: str
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    year: Optional[str] = None


@dataclass
class PaperContent:
    """Paper raw content"""
    file_path: str
    title: str = ""
    authors: List[str] = field(default_factory=list)
    abstract: str = ""
    full_text: str = ""
    sections: Dict[str, str] = field(default_factory=dict)
    figures: List[Figure] = field(default_factory=list)
    tables: List[Table] = field(default_factory=list)
    equations: List[Equation] = field(default_factory=list)
    references: List[Reference] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def filename(self) -> str:
        """Get filename"""
        import os
        return os.path.basename(self.file_path)


@dataclass
class SectionAnalysis:
    """Section analysis result"""
    section_type: str
    original_content: str
    key_points: List[str] = field(default_factory=list)
    summary: str = ""
    keywords: List[str] = field(default_factory=list)


@dataclass
class BackgroundAnalysis:
    """Background analysis"""
    research_field: str = ""
    problem_definition: str = ""
    motivation: str = ""
    existing_limitations: str = ""
    research_goals: str = ""


@dataclass
class TechnologyAnalysis:
    """Technology analysis"""
    method_overview: str = ""
    innovations: List[str] = field(default_factory=list)
    key_designs: List[str] = field(default_factory=list)
    implementation_details: str = ""
    architecture: str = ""
    architecture_type: str = ""  # MoE, Dense, Hybrid, Other
    model_scale: str = ""  # e.g., "671B total, 37B activated"
    model_type: str = ""  # LLM, Multimodal, Vision, Audio, etc.
    application_scenarios: List[str] = field(default_factory=list)  # e.g., ["dialogue", "image understanding", "code generation"]


@dataclass
class ExperimentAnalysis:
    """Experiment analysis"""
    datasets: List[str] = field(default_factory=list)
    metrics: List[str] = field(default_factory=list)
    baselines: List[str] = field(default_factory=list)
    setup: str = ""
    ablation_studies: str = ""


@dataclass
class ResultAnalysis:
    """Result analysis"""
    main_results: str = ""
    performance_improvements: str = ""
    key_findings: List[str] = field(default_factory=list)
    limitations: str = ""
    future_work: str = ""


@dataclass
class PaperAnalysis:
    """Paper analysis result"""
    paper: PaperContent
    background: BackgroundAnalysis = field(default_factory=BackgroundAnalysis)
    technology: TechnologyAnalysis = field(default_factory=TechnologyAnalysis)
    experiment: ExperimentAnalysis = field(default_factory=ExperimentAnalysis)
    result: ResultAnalysis = field(default_factory=ResultAnalysis)
    keywords: List[str] = field(default_factory=list)
    summary: str = ""
    sections: Dict[str, SectionAnalysis] = field(default_factory=dict)
    key_figures: List[int] = field(default_factory=list)  # Indices of key figures
    key_tables: List[int] = field(default_factory=list)   # Indices of key tables
    key_equations: List[int] = field(default_factory=list)  # Indices of key equations

    @property
    def title(self) -> str:
        return self.paper.title

    @property
    def authors(self) -> List[str]:
        return self.paper.authors


@dataclass
class ComparisonItem:
    """Comparison item"""
    dimension: str
    papers: Dict[str, str] = field(default_factory=dict)  # paper_title -> value


@dataclass
class TimelineItem:
    """Timeline item"""
    paper_title: str
    date: Optional[str] = None
    key_contribution: str = ""
    order: int = 0


@dataclass
class TrendItem:
    """Trend item"""
    trend_name: str
    description: str
    evidence: List[str] = field(default_factory=list)
    papers: List[str] = field(default_factory=list)


@dataclass
class AggregatedKnowledge:
    """Aggregated knowledge"""
    papers: List[PaperAnalysis]
    timeline: List[TimelineItem] = field(default_factory=list)
    comparison_matrix: List[ComparisonItem] = field(default_factory=list)
    common_themes: List[str] = field(default_factory=list)
    key_differences: List[str] = field(default_factory=list)
    trends: List[TrendItem] = field(default_factory=list)
    overall_summary: str = ""
    custom_analysis: Optional[str] = None  # Store custom analysis prompt if used


@dataclass
class Report:
    """Generated report"""
    report_type: str  # single, comparison, trend
    title: str
    content: str
    generated_at: datetime = field(default_factory=datetime.now)
    papers: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
