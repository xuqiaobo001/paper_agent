"""
Paper Reading Agent - Intelligent paper analysis tool

Supports batch reading of academic papers with automatic analysis and summarization
"""

__version__ = "1.0.0"

from .core import (
    # Config
    Config,
    get_config,
    reload_config,

    # Models
    PaperContent,
    PaperAnalysis,
    AggregatedKnowledge,
    Report,

    # Main functions
    parse_pdf,
    parse_pdfs,
    extract_paper_content,
    extract_papers_content,
    aggregate_papers,
    generate_report,
    save_report,
)

from .agent import PaperAgent

__all__ = [
    "__version__",
    "Config",
    "get_config",
    "reload_config",
    "PaperContent",
    "PaperAnalysis",
    "AggregatedKnowledge",
    "Report",
    "parse_pdf",
    "parse_pdfs",
    "extract_paper_content",
    "extract_papers_content",
    "aggregate_papers",
    "generate_report",
    "save_report",
    "PaperAgent",
]
