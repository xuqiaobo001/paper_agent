"""
Content Extractor Module
Responsible for extracting key information from papers using LLM
"""
import json
from typing import Optional, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from .models import (
    PaperContent, PaperAnalysis, SectionAnalysis,
    BackgroundAnalysis, TechnologyAnalysis, ExperimentAnalysis, ResultAnalysis
)
from .config import Config, get_config
from .structure_analyzer import StructureAnalyzer
from .llm_client import LLMHelper


class ContentExtractor:
    """Content Extractor"""

    # Four-dimension extraction prompts
    EXTRACTION_PROMPTS = {
        "background": """Analyze the research background of this paper and extract the following information:

Paper content:
{content}

Please return results in JSON format, including:
{{
    "research_field": "Research field and domain",
    "problem_definition": "Problem being solved",
    "motivation": "Research motivation",
    "existing_limitations": "Limitations of existing methods",
    "research_goals": "Research goals"
}}

Be concise and accurate in your extraction.""",

        "technology": """Analyze the technical methods of this paper and extract the following information:

Paper content:
{content}

Please return results in JSON format, including:
{{
    "method_overview": "Overall description of the method",
    "innovations": ["Innovation 1", "Innovation 2", ...],
    "key_designs": ["Key design 1", "Key design 2", ...],
    "implementation_details": "Important implementation details",
    "architecture": "Model/system architecture description",
    "architecture_type": "Specify if the model is: MoE (Mixture-of-Experts), Dense, Hybrid, or Other. IMPORTANT: Be precise - check for keywords like 'MoE', 'Mixture-of-Experts', 'sparse activation', 'expert routing', 'total parameters vs activated parameters'. If a model is based on another model (e.g., 'built on Model-X'), inherit that model's architecture type.",
    "model_scale": "Total parameters and activated parameters (if MoE architecture). Example format: 'XXB total, YYB activated per token' or 'ZZB parameters' for dense models",
    "model_type": "CRITICAL - Specify the PRIMARY model type. Choose ONE from: LLM (text-only language model), Multimodal (handles multiple modalities like vision+language, audio+text), Vision (image/video-focused), Audio (speech/sound-focused), Code (specialized for code), Reasoning (specialized for reasoning tasks), or Other. IMPORTANT: Do NOT confuse models from the same series - check the paper content carefully. For example, Model-VL is Multimodal while Model-LLM is LLM.",
    "application_scenarios": ["Primary application 1", "Primary application 2", ...] - List the MAIN intended use cases. Examples: "text generation", "image understanding", "visual question answering", "code generation", "mathematical reasoning", "multimodal dialogue", "video analysis", etc.
}}

Focus on core technical contributions. Pay special attention to:
1. Correctly identifying the architecture type
2. DISTINGUISHING the model type - especially between LLM and Multimodal models
3. Identifying the PRIMARY application scenarios based on the paper's focus""",

        "experiment": """Analyze the experimental design of this paper and extract the following information:

Paper content:
{content}

Please return results in JSON format, including:
{{
    "datasets": ["Dataset 1", "Dataset 2", ...],
    "metrics": ["Evaluation metric 1", "Evaluation metric 2", ...],
    "baselines": ["Baseline method 1", "Baseline method 2", ...],
    "setup": "Experimental setup description",
    "ablation_studies": "Description of ablation studies (if any)"
}}

Include specific dataset names and metrics.""",

        "result": """Analyze the results of this paper and extract the following information:

Paper content:
{content}

Please return results in JSON format, including:
{{
    "main_results": "Key experimental results",
    "performance_improvements": "Performance improvements compared to baselines",
    "key_findings": ["Key finding 1", "Key finding 2", ...],
    "limitations": "Known limitations of the method",
    "future_work": "Future work directions"
}}

Summarize the results accurately.""",
    }

    # Section analysis prompt
    SECTION_ANALYSIS_PROMPT = """Analyze this section and extract key information:

Section type: {section_type}
Content:
{content}

Please return results in JSON format, including:
{{
    "key_points": ["Key point 1", "Key point 2", ...],
    "summary": "Brief summary",
    "keywords": ["Keyword 1", "Keyword 2", ...]
}}"""

    # Keyword extraction prompt
    KEYWORDS_PROMPT = """Extract {num_keywords} core keywords from the following paper abstract and content.

Title: {title}
Abstract: {abstract}

Main content:
{content}

Please return results in JSON format:
{{
    "keywords": ["keyword1", "keyword2", ...]
}}

Keywords should cover:
1. Research field/domain
2. Core methods/techniques
3. Key contributions
4. Application areas"""

    # Summary generation prompt
    SUMMARY_PROMPT = """Generate a comprehensive summary of this paper in {language}.

Paper title: {title}
Abstract: {abstract}

Main analysis results:
- Research background: {background}
- Core technology: {technology}
- Experimental design: {experiment}
- Main results: {result}

Please generate a {detail_level} summary covering:
1. Research problem and motivation
2. Proposed method and innovations
3. Experimental validation and main results
4. Paper contributions and significance

Output the summary directly, no JSON format needed."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or get_config()
        self.extractor_config = self.config.content_extractor
        self.structure_analyzer = StructureAnalyzer(self.config)
        self.llm_helper = LLMHelper(self.config)

    def extract(self, paper: PaperContent) -> PaperAnalysis:
        """Comprehensively extract paper content"""
        # Analyze paper structure
        sections = self.structure_analyzer.analyze(paper)

        # Create analysis result object
        analysis = PaperAnalysis(paper=paper)

        # Extract each dimension in parallel
        dimensions = self.extractor_config.dimensions
        dimension_contents = self._prepare_dimension_contents(paper, sections)

        if self.config.parallel.enabled:
            with ThreadPoolExecutor(max_workers=min(len(dimensions), self.config.parallel.max_workers)) as executor:
                futures = {}
                for dim in dimensions:
                    if dim in dimension_contents:
                        futures[executor.submit(self._extract_dimension, dim, dimension_contents[dim])] = dim

                for future in as_completed(futures):
                    dim = futures[future]
                    try:
                        result = future.result()
                        self._set_dimension_result(analysis, dim, result)
                    except Exception as e:
                        print(f"Failed to extract {dim}: {e}")
        else:
            for dim in dimensions:
                if dim in dimension_contents:
                    try:
                        result = self._extract_dimension(dim, dimension_contents[dim])
                        self._set_dimension_result(analysis, dim, result)
                    except Exception as e:
                        print(f"Failed to extract {dim}: {e}")

        # Extract keywords
        if self.extractor_config.extract_keywords:
            analysis.keywords = self._extract_keywords(paper)

        # Generate summary
        analysis.summary = self._generate_summary(paper, analysis)

        # Identify key figures, tables, and equations
        self._identify_key_resources(paper, analysis)

        # Analyze sections
        analysis.sections = self._analyze_sections(sections)

        return analysis

    def extract_quick(self, paper: PaperContent) -> PaperAnalysis:
        """Quick extraction - only extract keywords and brief summary"""
        analysis = PaperAnalysis(paper=paper)

        # Extract keywords
        if self.extractor_config.extract_keywords:
            analysis.keywords = self._extract_keywords(paper)

        # Generate brief summary
        prompt = f"""Generate a brief summary of this paper (around 200 words):

Title: {paper.title}
Abstract: {paper.abstract}

Include: main problem, proposed method, and key results."""

        analysis.summary = self.llm_helper.ask(prompt)

        return analysis

    def _prepare_dimension_contents(self, paper: PaperContent, sections: Dict[str, str]) -> Dict[str, str]:
        """Prepare content for each dimension extraction"""
        contents = {}

        # Background: abstract + introduction + related work
        background_parts = [paper.abstract]
        if "introduction" in sections:
            background_parts.append(sections["introduction"][:2000])
        if "related_work" in sections:
            background_parts.append(sections["related_work"][:1000])
        contents["background"] = "\n\n".join(background_parts)

        # Technology: method + architecture parts
        # ENHANCED: Smart sampling to capture architecture info
        tech_parts = []
        if "method" in sections:
            method_text = sections["method"]

            # Take first part (overview)
            tech_parts.append(method_text[:1500])

            # Search for architecture-critical paragraphs using GENERIC keywords
            arch_keywords = [
                # Model initialization/heritage keywords
                'base model', 'built on', 'based on', 'starting from',
                'initialized from', 'inherit', 'extend',
                # Architecture type keywords
                'architecture', 'moe', 'mixture-of-experts', 'mixture of experts',
                'dense', 'sparse', 'transformer', 'attention',
                # Model scale keywords
                'parameters', 'param', 'billion', 'million',
                'total parameters', 'activated parameters',
                # Expert-related keywords
                'expert', 'routing', 'gating', 'load balancing'
            ]

            # Split into paragraphs and find architecture-related ones
            paragraphs = method_text.split('\n\n')
            for para in paragraphs:
                para_lower = para.lower()
                # Check if paragraph contains architecture-related information
                if any(keyword in para_lower for keyword in arch_keywords):
                    # Found architecture-related paragraph
                    if para not in tech_parts[0]:  # Avoid duplication
                        tech_parts.append(para[:500])  # Add up to 500 chars of this paragraph
                        if sum(len(p) for p in tech_parts) > 2500:  # Soft limit
                            break
        elif "abstract" in sections:
            tech_parts.append(sections.get("abstract", paper.abstract))

        # Combine and limit total length
        contents["technology"] = "\n\n".join(tech_parts)[:self.extractor_config.max_length_per_dimension]

        # Experiment: experiment section
        if "experiment" in sections:
            contents["experiment"] = sections["experiment"][:self.extractor_config.max_length_per_dimension]
        else:
            contents["experiment"] = paper.full_text[:self.extractor_config.max_length_per_dimension]

        # Result: result + conclusion sections
        result_parts = []
        if "result" in sections:
            result_parts.append(sections["result"])
        if "conclusion" in sections:
            result_parts.append(sections["conclusion"])
        if result_parts:
            contents["result"] = "\n\n".join(result_parts)[:self.extractor_config.max_length_per_dimension]
        else:
            contents["result"] = paper.abstract

        return contents

    def _extract_dimension(self, dimension: str, content: str) -> Dict[str, Any]:
        """Extract single dimension"""
        if dimension not in self.EXTRACTION_PROMPTS:
            return {}

        prompt = self.EXTRACTION_PROMPTS[dimension].format(content=content)

        try:
            return self.llm_helper.extract_json(prompt)
        except Exception as e:
            print(f"Failed to extract {dimension}: {e}")
            return {}

    def _set_dimension_result(self, analysis: PaperAnalysis, dimension: str, result: Dict[str, Any]) -> None:
        """Set dimension extraction result to analysis object"""
        if dimension == "background":
            analysis.background = BackgroundAnalysis(
                research_field=result.get("research_field", ""),
                problem_definition=result.get("problem_definition", ""),
                motivation=result.get("motivation", ""),
                existing_limitations=result.get("existing_limitations", ""),
                research_goals=result.get("research_goals", ""),
            )
        elif dimension == "technology":
            analysis.technology = TechnologyAnalysis(
                method_overview=result.get("method_overview", ""),
                innovations=result.get("innovations", []),
                key_designs=result.get("key_designs", []),
                implementation_details=result.get("implementation_details", ""),
                architecture=result.get("architecture", ""),
            )
        elif dimension == "experiment":
            analysis.experiment = ExperimentAnalysis(
                datasets=result.get("datasets", []),
                metrics=result.get("metrics", []),
                baselines=result.get("baselines", []),
                setup=result.get("setup", ""),
                ablation_studies=result.get("ablation_studies", ""),
            )
        elif dimension == "result":
            analysis.result = ResultAnalysis(
                main_results=result.get("main_results", ""),
                performance_improvements=result.get("performance_improvements", ""),
                key_findings=result.get("key_findings", []),
                limitations=result.get("limitations", ""),
                future_work=result.get("future_work", ""),
            )

    def _extract_keywords(self, paper: PaperContent) -> List[str]:
        """Extract keywords"""
        prompt = self.KEYWORDS_PROMPT.format(
            num_keywords=self.extractor_config.num_keywords,
            title=paper.title,
            abstract=paper.abstract,
            content=paper.full_text[:3000],
        )

        try:
            result = self.llm_helper.extract_json(prompt)
            return result.get("keywords", [])
        except Exception as e:
            print(f"Failed to extract keywords: {e}")
            return []

    def _generate_summary(self, paper: PaperContent, analysis: PaperAnalysis) -> str:
        """Generate paper summary"""
        # Determine language - force chinese or english only
        language = self.config.report_generator.language.lower()
        if language not in ["chinese", "english"]:
            language = "english"  # Default to english if invalid

        # Map to natural language name
        language_name = "Chinese" if language == "chinese" else "English"

        # Determine detail level
        detail_level_map = {
            "brief": "brief (200-300 words)" if language == "english" else "简短（200-300字）",
            "detailed": "detailed (400-600 words)" if language == "english" else "详细（400-600字）",
            "comprehensive": "comprehensive (800-1000 words)" if language == "english" else "全面（800-1000字）",
        }
        detail_level = detail_level_map.get(
            self.config.report_generator.summary_level,
            "detailed (400-600 words)" if language == "english" else "详细（400-600字）"
        )

        prompt = self.SUMMARY_PROMPT.format(
            language=language_name,
            title=paper.title,
            abstract=paper.abstract,
            background=analysis.background.motivation if analysis.background else "",
            technology=analysis.technology.method_overview if analysis.technology else "",
            experiment=", ".join(analysis.experiment.datasets) if analysis.experiment else "",
            result=analysis.result.main_results if analysis.result else "",
            detail_level=detail_level,
        )

        return self.llm_helper.ask(prompt)

    def _analyze_sections(self, sections: Dict[str, str]) -> Dict[str, SectionAnalysis]:
        """Analyze each section"""
        result = {}

        # Only analyze main sections
        main_sections = ["abstract", "introduction", "method", "experiment", "result", "conclusion"]

        for section_type in main_sections:
            if section_type in sections and sections[section_type]:
                content = sections[section_type][:2000]
                prompt = self.SECTION_ANALYSIS_PROMPT.format(
                    section_type=section_type,
                    content=content,
                )

                try:
                    analysis_result = self.llm_helper.extract_json(prompt)
                    result[section_type] = SectionAnalysis(
                        section_type=section_type,
                        original_content=content,
                        key_points=analysis_result.get("key_points", []),
                        summary=analysis_result.get("summary", ""),
                        keywords=analysis_result.get("keywords", []),
                    )
                except Exception as e:
                    print(f"Failed to analyze section {section_type}: {e}")

        return result

    def _identify_key_resources(self, paper: PaperContent, analysis: PaperAnalysis) -> None:
        """
        Identify key figures, tables, and equations that should be included in the report

        Uses LLM to determine which visual elements are most important
        """
        # Prepare resource information
        resources_info = []

        if paper.figures:
            resources_info.append(f"\n**Available Figures ({len(paper.figures)} total):**")
            for idx, fig in enumerate(paper.figures, 1):
                resources_info.append(f"  Figure {idx}: {fig.caption} (Page {fig.page})")

        if paper.tables:
            resources_info.append(f"\n**Available Tables ({len(paper.tables)} total):**")
            for idx, table in enumerate(paper.tables, 1):
                caption = table.caption if table.caption else f"Table on page {table.page}"
                resources_info.append(f"  Table {idx}: {caption}")

        if paper.equations:
            resources_info.append(f"\n**Available Equations ({len(paper.equations)} total):**")
            for idx, eq in enumerate(paper.equations, 1):
                eq_desc = eq.equation_number if eq.equation_number else f"Equation {idx}"
                resources_info.append(f"  {eq_desc}: {eq.equation_text[:80]}...")

        if not resources_info:
            return  # No resources to identify

        resources_text = "\n".join(resources_info)

        # Construct prompt
        prompt = f"""Based on the paper analysis, identify the most important figures, tables, and equations that should be included in the summary report.

Paper: {paper.title}

Paper Summary:
{analysis.summary[:500]}...

Core Technology:
{analysis.technology.method_overview if analysis.technology else "N/A"}

Main Results:
{analysis.result.main_results if analysis.result else "N/A"}

{resources_text}

Please identify which resources are KEY/CRITICAL for understanding this paper. Select up to:
- 3 most important figures
- 3 most important tables
- 5 most important equations

Return results in JSON format:
{{
    "key_figures": [1, 2],  // Figure indices (1-based)
    "key_tables": [1],      // Table indices (1-based)
    "key_equations": [1, 3, 5],  // Equation indices (1-based)
    "reasoning": "Brief explanation of why these resources are key"
}}

If a category has no key resources, return an empty list []."""

        try:
            result = self.llm_helper.extract_json(prompt)

            # Store the identified key resources
            analysis.key_figures = result.get("key_figures", [])
            analysis.key_tables = result.get("key_tables", [])
            analysis.key_equations = result.get("key_equations", [])

            if result.get("reasoning"):
                print(f"Resource selection reasoning: {result['reasoning']}")

        except Exception as e:
            print(f"Failed to identify key resources: {e}")
            # Fallback: select first few of each if available
            analysis.key_figures = list(range(1, min(4, len(paper.figures) + 1)))
            analysis.key_tables = list(range(1, min(4, len(paper.tables) + 1)))
            analysis.key_equations = list(range(1, min(6, len(paper.equations) + 1)))


def extract_paper_content(paper: PaperContent, config: Optional[Config] = None) -> PaperAnalysis:
    """Convenience function: Extract paper content"""
    extractor = ContentExtractor(config)
    return extractor.extract(paper)


def extract_papers_content(papers: List[PaperContent], config: Optional[Config] = None) -> List[PaperAnalysis]:
    """Convenience function: Batch extract paper content"""
    config = config or get_config()
    extractor = ContentExtractor(config)

    results = []
    if config.parallel.enabled:
        with ThreadPoolExecutor(max_workers=config.parallel.max_workers) as executor:
            futures = {executor.submit(extractor.extract, paper): paper for paper in papers}
            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    paper = futures[future]
                    print(f"Failed to extract {paper.title}: {e}")
    else:
        for paper in papers:
            try:
                results.append(extractor.extract(paper))
            except Exception as e:
                print(f"Failed to extract {paper.title}: {e}")

    return results
