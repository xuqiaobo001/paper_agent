"""
Configuration Management Module
Responsible for loading and managing configuration files
"""
import os
import re
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class LLMConfig:
    """LLM Configuration"""
    provider: str = "openai"
    model: str = "gpt-4o"
    api_key: str = ""
    api_base: str = ""
    temperature: float = 0.3
    max_tokens: int = 4096
    timeout: int = 120
    max_retries: int = 3
    retry_delay: int = 2


@dataclass
class PDFParserConfig:
    """PDF Parser Configuration"""
    engine: str = "pymupdf"
    extract_images: bool = False
    extract_tables: bool = True
    max_pages: int = 0
    encoding: str = "utf-8"


@dataclass
class StructureAnalyzerConfig:
    """Structure Analyzer Configuration"""
    section_patterns: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class ContentExtractorConfig:
    """Content Extractor Configuration"""
    dimensions: List[str] = field(default_factory=lambda: ["background", "technology", "experiment", "result"])
    max_length_per_dimension: int = 2000
    extract_keywords: bool = True
    num_keywords: int = 10


@dataclass
class KnowledgeAggregatorConfig:
    """Knowledge Aggregator Configuration"""
    comparison_dimensions: List[str] = field(default_factory=lambda: ["architecture", "training_method", "performance"])
    generate_timeline: bool = True
    analyze_trends: bool = True


@dataclass
class ReportGeneratorConfig:
    """Report Generator Configuration"""
    output_format: str = "markdown"
    language: str = "english"
    include_quotes: bool = True
    summary_level: str = "detailed"
    template_dir: str = "templates"


@dataclass
class ParallelConfig:
    """Parallel Processing Configuration"""
    enabled: bool = True
    max_workers: int = 4


@dataclass
class CacheConfig:
    """Cache Configuration"""
    enabled: bool = True
    cache_dir: str = ".cache"
    expire_hours: int = 24


@dataclass
class LoggingConfig:
    """Logging Configuration"""
    level: str = "INFO"
    file: str = "paper_agent.log"
    console: bool = True


class Config:
    """Configuration Manager"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._find_config_file()
        self._raw_config: Dict[str, Any] = {}

        # Module configurations
        self.llm = LLMConfig()
        self.pdf_parser = PDFParserConfig()
        self.structure_analyzer = StructureAnalyzerConfig()
        self.content_extractor = ContentExtractorConfig()
        self.knowledge_aggregator = KnowledgeAggregatorConfig()
        self.report_generator = ReportGeneratorConfig()
        self.parallel = ParallelConfig()
        self.cache = CacheConfig()
        self.logging = LoggingConfig()

        # LLM providers information
        self.llm_providers: Dict[str, Any] = {}

        if self.config_path and os.path.exists(self.config_path):
            self.load()

    def _find_config_file(self) -> Optional[str]:
        """Find configuration file"""
        search_paths = [
            "./config.yaml",
            "./paper_agent/config.yaml",
            "../config.yaml",
            os.path.expanduser("~/.paper_agent/config.yaml"),
        ]

        for path in search_paths:
            if os.path.exists(path):
                return path
        return None

    def _resolve_env_vars(self, value: Any) -> Any:
        """
        Resolve environment variables in configuration values.

        Supports two formats:
        - ${VAR_NAME} - Uses environment variable, empty string if not set
        - ${VAR_NAME:default} - Uses environment variable, or default if not set

        Examples:
            ${OPENAI_API_KEY} -> value of OPENAI_API_KEY or ""
            ${LLM_PROVIDER:openai} -> value of LLM_PROVIDER or "openai"
            ${LLM_API_BASE:} -> value of LLM_API_BASE or ""
        """
        if isinstance(value, str):
            # Match ${VAR_NAME} or ${VAR_NAME:default} format
            pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'

            def replace_env_var(match):
                var_name = match.group(1)
                default_value = match.group(2) if match.group(2) is not None else ""
                return os.environ.get(var_name, default_value)

            return re.sub(pattern, replace_env_var, value)
        elif isinstance(value, dict):
            return {k: self._resolve_env_vars(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._resolve_env_vars(v) for v in value]
        return value

    def load(self) -> None:
        """Load configuration file"""
        if not self.config_path or not os.path.exists(self.config_path):
            return

        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._raw_config = yaml.safe_load(f) or {}

        # Resolve environment variables
        self._raw_config = self._resolve_env_vars(self._raw_config)

        # Load module configurations
        self._load_llm_config()
        self._load_pdf_parser_config()
        self._load_structure_analyzer_config()
        self._load_content_extractor_config()
        self._load_knowledge_aggregator_config()
        self._load_report_generator_config()
        self._load_parallel_config()
        self._load_cache_config()
        self._load_logging_config()

        # Load providers information
        self.llm_providers = self._raw_config.get("llm_providers", {})

    def _load_llm_config(self) -> None:
        """
        Load LLM configuration.

        The configuration is resolved in the following priority:
        1. Explicit values in llm section
        2. Provider preset values from llm_providers section
        3. Environment variables (via api_key_env in provider preset)
        4. Default values
        """
        llm_cfg = self._raw_config.get("llm", {})
        providers_cfg = self._raw_config.get("llm_providers", {})

        provider = llm_cfg.get("provider", "openai")
        provider_preset = providers_cfg.get(provider, {})

        # Resolve API key: explicit value > provider env var > empty
        api_key = llm_cfg.get("api_key", "")
        if not api_key and provider_preset:
            api_key_env = provider_preset.get("api_key_env", "")
            if api_key_env:
                api_key = os.environ.get(api_key_env, "")

        # Resolve API base: explicit value > provider preset > empty
        api_base = llm_cfg.get("api_base", "")
        if not api_base and provider_preset:
            api_base = provider_preset.get("api_base", "")

        self.llm = LLMConfig(
            provider=provider,
            model=llm_cfg.get("model", "gpt-4o"),
            api_key=api_key,
            api_base=api_base,
            temperature=llm_cfg.get("temperature", 0.3),
            max_tokens=llm_cfg.get("max_tokens", 4096),
            timeout=llm_cfg.get("timeout", 120),
            max_retries=llm_cfg.get("max_retries", 3),
            retry_delay=llm_cfg.get("retry_delay", 2),
        )

    def _load_pdf_parser_config(self) -> None:
        """Load PDF parser configuration"""
        cfg = self._raw_config.get("pdf_parser", {})
        self.pdf_parser = PDFParserConfig(
            engine=cfg.get("engine", "pymupdf"),
            extract_images=cfg.get("extract_images", False),
            extract_tables=cfg.get("extract_tables", True),
            max_pages=cfg.get("max_pages", 0),
            encoding=cfg.get("encoding", "utf-8"),
        )

    def _load_structure_analyzer_config(self) -> None:
        """Load structure analyzer configuration"""
        cfg = self._raw_config.get("structure_analyzer", {})
        self.structure_analyzer = StructureAnalyzerConfig(
            section_patterns=cfg.get("section_patterns", {}),
        )

    def _load_content_extractor_config(self) -> None:
        """Load content extractor configuration"""
        cfg = self._raw_config.get("content_extractor", {})
        self.content_extractor = ContentExtractorConfig(
            dimensions=cfg.get("dimensions", ["background", "technology", "experiment", "result"]),
            max_length_per_dimension=cfg.get("max_length_per_dimension", 2000),
            extract_keywords=cfg.get("extract_keywords", True),
            num_keywords=cfg.get("num_keywords", 10),
        )

    def _load_knowledge_aggregator_config(self) -> None:
        """Load knowledge aggregator configuration"""
        cfg = self._raw_config.get("knowledge_aggregator", {})
        self.knowledge_aggregator = KnowledgeAggregatorConfig(
            comparison_dimensions=cfg.get("comparison_dimensions", ["architecture", "training_method", "performance"]),
            generate_timeline=cfg.get("generate_timeline", True),
            analyze_trends=cfg.get("analyze_trends", True),
        )

    def _load_report_generator_config(self) -> None:
        """Load report generator configuration"""
        cfg = self._raw_config.get("report_generator", {})
        self.report_generator = ReportGeneratorConfig(
            output_format=cfg.get("output_format", "markdown"),
            language=cfg.get("language", "english"),
            include_quotes=cfg.get("include_quotes", True),
            summary_level=cfg.get("summary_level", "detailed"),
            template_dir=cfg.get("template_dir", "templates"),
        )

    def _load_parallel_config(self) -> None:
        """Load parallel processing configuration"""
        cfg = self._raw_config.get("parallel", {})
        self.parallel = ParallelConfig(
            enabled=cfg.get("enabled", True),
            max_workers=cfg.get("max_workers", 4),
        )

    def _load_cache_config(self) -> None:
        """Load cache configuration"""
        cfg = self._raw_config.get("cache", {})
        self.cache = CacheConfig(
            enabled=cfg.get("enabled", True),
            cache_dir=cfg.get("cache_dir", ".cache"),
            expire_hours=cfg.get("expire_hours", 24),
        )

    def _load_logging_config(self) -> None:
        """Load logging configuration"""
        cfg = self._raw_config.get("logging", {})
        self.logging = LoggingConfig(
            level=cfg.get("level", "INFO"),
            file=cfg.get("file", "paper_agent.log"),
            console=cfg.get("console", True),
        )

    def get_llm_api_base(self) -> str:
        """Get LLM API base URL"""
        if self.llm.api_base:
            return self.llm.api_base

        provider_config = self.llm_providers.get(self.llm.provider, {})
        return provider_config.get("api_base", "")

    def save(self, path: Optional[str] = None) -> None:
        """Save configuration to file"""
        save_path = path or self.config_path
        if not save_path:
            raise ValueError("No config path specified")

        with open(save_path, 'w', encoding='utf-8') as f:
            yaml.dump(self._raw_config, f, allow_unicode=True, default_flow_style=False)

    def update_llm(self, **kwargs) -> None:
        """Update LLM configuration"""
        for key, value in kwargs.items():
            if hasattr(self.llm, key):
                setattr(self.llm, key, value)

    def __repr__(self) -> str:
        return f"Config(llm={self.llm.provider}:{self.llm.model})"


# Global configuration instance
_config: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    """Get global configuration instance"""
    global _config
    if _config is None or config_path:
        _config = Config(config_path)
    return _config


def reload_config(config_path: Optional[str] = None) -> Config:
    """Reload configuration"""
    global _config
    _config = Config(config_path)
    return _config
