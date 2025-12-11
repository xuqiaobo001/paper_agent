"""
Paper Reading Agent - Core Modules
"""

from .config import Config, get_config, reload_config
from .models import (
    PaperContent, PaperAnalysis,
    BackgroundAnalysis, TechnologyAnalysis,
    ExperimentAnalysis, ResultAnalysis,
    AggregatedKnowledge, Report
)
from .pdf_parser import PDFParser, parse_pdf, parse_pdfs
from .structure_analyzer import StructureAnalyzer, analyze_structure
from .llm_client import LLMClient, LLMHelper, create_llm_client, get_llm_helper
from .content_extractor import ContentExtractor, extract_paper_content, extract_papers_content
from .knowledge_aggregator import KnowledgeAggregator, aggregate_papers
from .report_generator import ReportGenerator, generate_report, save_report

__all__ = [
    # Config
    "Config",
    "get_config",
    "reload_config",

    # Models
    "PaperContent",
    "PaperAnalysis",
    "BackgroundAnalysis",
    "TechnologyAnalysis",
    "ExperimentAnalysis",
    "ResultAnalysis",
    "AggregatedKnowledge",
    "Report",

    # PDF Parser
    "PDFParser",
    "parse_pdf",
    "parse_pdfs",

    # Structure Analyzer
    "StructureAnalyzer",
    "analyze_structure",

    # LLM Client
    "LLMClient",
    "LLMHelper",
    "create_llm_client",
    "get_llm_helper",

    # Content Extractor
    "ContentExtractor",
    "extract_paper_content",
    "extract_papers_content",

    # Knowledge Aggregator
    "KnowledgeAggregator",
    "aggregate_papers",

    # Report Generator
    "ReportGenerator",
    "generate_report",
    "save_report",
]
