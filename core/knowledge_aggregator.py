"""
Knowledge Aggregator Module
Responsible for aggregating and comparing knowledge from multiple papers
"""
import json
from typing import Optional, List, Dict, Any

from .models import (
    PaperAnalysis, AggregatedKnowledge,
    ComparisonItem, TimelineItem, TrendItem
)
from .config import Config, get_config
from .llm_client import LLMHelper


class KnowledgeAggregator:
    """Knowledge Aggregator"""

    # Comparison prompt
    COMPARISON_PROMPT = """Compare and analyze the following papers:

{papers_info}

Please analyze from the "{dimension}" dimension and return results in JSON format:
{{
    "comparison": {{
        "paper1_title": "value/description",
        "paper2_title": "value/description",
        ...
    }},
    "similarities": ["Similarity 1", "Similarity 2", ...],
    "differences": ["Difference 1", "Difference 2", ...],
    "analysis": "Overall analysis"
}}

Be specific and detailed in your comparison."""

    # Architecture-specific comparison prompt
    ARCHITECTURE_COMPARISON_PROMPT = """Compare and analyze the MODEL ARCHITECTURES of the following papers:

{papers_info}

CRITICAL: Pay special attention to the architecture type. Check if each model is:
- **MoE (Mixture-of-Experts)**: Keywords like "mixture-of-experts", "MoE", "sparse activation", "expert routing", "X total parameters, Y activated parameters"
- **Dense**: Traditional transformer architecture where all parameters are activated
- **Hybrid**: Combination of MoE and Dense layers
- **Other**: Other architecture types

If a paper mentions that a model is "based on" or "built on" another model, **inherit that base model's architecture type**.

Please return results in JSON format:
{{
    "comparison": {{
        "paper1_title": "Architecture description including type (MoE/Dense/Hybrid/Other) and scale",
        "paper2_title": "Architecture description including type (MoE/Dense/Hybrid/Other) and scale",
        ...
    }},
    "similarities": ["Similarity 1", "Similarity 2", ...],
    "differences": ["Difference 1", "Difference 2", ...],
    "analysis": "Overall analysis focusing on architectural differences"
}}

Example response for comparison:
{{
    "comparison": {{
        "DeepSeek-V3": "MoE architecture with 671B total parameters, 37B activated per token",
        "DeepSeek-V3.2": "MoE architecture (inherited from DeepSeek-V3), adds DeepSeek Sparse Attention"
    }},
    ...
}}

Be precise and accurate. Double-check architecture types."""

    # Timeline construction prompt
    TIMELINE_PROMPT = """Construct a technology development timeline based on the following papers:

{papers_info}

Consider:
1. Publication time (if available)
2. Technical evolution relationships
3. Citation relationships

Please return results in JSON format:
{{
    "timeline": [
        {{
            "paper_title": "Paper title",
            "date": "Date (can be inferred, format: YYYY or YYYY-MM)",
            "key_contribution": "Main contribution of this paper",
            "order": 1
        }},
        ...
    ]
}}

Order should reflect logical development of the technology, not necessarily chronological."""

    # Trend analysis prompt
    TREND_PROMPT = """Analyze the technology trends shown across the following papers:

{papers_info}

Please identify 3-5 main trends and return results in JSON format:
{{
    "trends": [
        {{
            "trend_name": "Trend name",
            "description": "Detailed description",
            "evidence": ["Evidence 1 (which paper demonstrates this)", ...],
            "papers": ["Related paper 1", ...]
        }},
        ...
    ],
    "common_themes": ["Theme 1", "Theme 2", ...],
    "key_differences": ["Difference 1", "Difference 2", ...],
    "future_directions": ["Direction 1", "Direction 2", ...]
}}"""

    # Overall summary prompt
    OVERALL_SUMMARY_PROMPT = """Based on the analysis results of the following papers, generate an overall summary:

{papers_info}

Comparison results:
{comparison_summary}

Trend analysis:
{trends_summary}

Please generate a comprehensive summary (300-500 words) in {language}, including:
1. Main research theme of this paper collection
2. Key technical developments and evolution
3. Current research hotspots and challenges
4. Future research directions

Output the summary directly, no JSON format needed."""

    # Custom analysis prompt
    CUSTOM_ANALYSIS_PROMPT = """Based on the following papers, please analyze according to the user's requirement:

User Requirement: {custom_prompt}

Papers Information:
{papers_info}

Please provide a comprehensive analysis based on the user's requirement. Output in {language}, be detailed and specific."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or get_config()
        self.aggregator_config = self.config.knowledge_aggregator
        self.llm_helper = LLMHelper(self.config)

    def aggregate(self, papers: List[PaperAnalysis], custom_prompt: Optional[str] = None) -> AggregatedKnowledge:
        """Aggregate knowledge from multiple papers

        Args:
            papers: List of paper analyses
            custom_prompt: Custom analysis requirement (if provided, uses custom analysis mode)
        """
        if not papers:
            return AggregatedKnowledge(papers=[])

        if len(papers) == 1:
            # Single paper, return directly without comparison
            return AggregatedKnowledge(
                papers=papers,
                overall_summary=papers[0].summary,
            )

        # Prepare paper information summary
        papers_info = self._prepare_papers_info(papers)

        # If custom prompt provided, use custom analysis mode
        if custom_prompt:
            return self._custom_analysis(papers, papers_info, custom_prompt)

        # Otherwise, use default analysis mode
        return self._default_analysis(papers, papers_info)

    def _custom_analysis(self, papers: List[PaperAnalysis], papers_info: str, custom_prompt: str) -> AggregatedKnowledge:
        """Custom analysis mode based on user's requirement"""
        print(f"Using custom analysis mode: {custom_prompt}")

        # Determine language - force chinese or english only
        language = self.config.report_generator.language.lower()
        if language not in ["chinese", "english"]:
            language = "english"  # Default to english if invalid

        # Map to natural language name
        language_name = "Chinese" if language == "chinese" else "English"

        # Generate custom analysis
        prompt = self.CUSTOM_ANALYSIS_PROMPT.format(
            custom_prompt=custom_prompt,
            papers_info=papers_info,
            language=language_name,
        )

        custom_summary = self.llm_helper.ask(prompt)

        return AggregatedKnowledge(
            papers=papers,
            overall_summary=custom_summary,
            common_themes=[],
            key_differences=[],
            custom_analysis=custom_prompt,  # Store custom prompt for reference
        )

    def _default_analysis(self, papers: List[PaperAnalysis], papers_info: str) -> AggregatedKnowledge:
        """Default analysis mode with comparison matrix and trends"""

        # Build comparison matrix
        comparison_matrix = []
        common_themes = []
        key_differences = []

        if self.aggregator_config.comparison_dimensions:
            comparison_matrix, common_themes, key_differences = self._build_comparison_matrix(papers, papers_info)

        # Build timeline
        timeline = []
        if self.aggregator_config.generate_timeline:
            timeline = self._build_timeline(papers_info)

        # Analyze trends
        trends = []
        if self.aggregator_config.analyze_trends:
            trends_result = self._analyze_trends(papers_info)
            trends = trends_result.get("trends", [])
            if not common_themes:
                common_themes = trends_result.get("common_themes", [])
            if not key_differences:
                key_differences = trends_result.get("key_differences", [])

        # Generate overall summary
        overall_summary = self._generate_overall_summary(
            papers_info,
            comparison_matrix,
            trends
        )

        return AggregatedKnowledge(
            papers=papers,
            timeline=timeline,
            comparison_matrix=comparison_matrix,
            common_themes=common_themes,
            key_differences=key_differences,
            trends=trends,
            overall_summary=overall_summary,
        )

    def _prepare_papers_info(self, papers: List[PaperAnalysis]) -> str:
        """Prepare paper information summary"""
        info_parts = []

        for i, paper in enumerate(papers, 1):
            # Extract architecture info if available
            arch_info = ""
            if paper.technology:
                if hasattr(paper.technology, 'architecture') and paper.technology.architecture:
                    arch_info = f"\nArchitecture: {paper.technology.architecture}"
                if hasattr(paper.technology, 'architecture_type'):
                    arch_info += f"\nArchitecture Type: {paper.technology.architecture_type}"
                if hasattr(paper.technology, 'model_scale'):
                    arch_info += f"\nModel Scale: {paper.technology.model_scale}"

            info = f"""Paper {i}: {paper.title}
Authors: {', '.join(paper.authors) if paper.authors else 'Unknown'}
Abstract: {paper.paper.abstract[:500]}...

Research Background: {paper.background.motivation if paper.background else 'N/A'}
Core Method: {paper.technology.method_overview if paper.technology else 'N/A'}{arch_info}
Innovations: {', '.join(paper.technology.innovations) if paper.technology and paper.technology.innovations else 'N/A'}
Main Results: {paper.result.main_results if paper.result else 'N/A'}
Keywords: {', '.join(paper.keywords) if paper.keywords else 'N/A'}
"""
            info_parts.append(info)

        return "\n---\n".join(info_parts)

    def _build_comparison_matrix(self, papers: List[PaperAnalysis], papers_info: str) -> tuple:
        """Build comparison matrix"""
        comparison_matrix = []
        all_similarities = []
        all_differences = []

        for dimension in self.aggregator_config.comparison_dimensions:
            # Use architecture-specific prompt for architecture dimension
            if dimension.lower() == "architecture":
                prompt = self.ARCHITECTURE_COMPARISON_PROMPT.format(
                    papers_info=papers_info,
                )
            else:
                prompt = self.COMPARISON_PROMPT.format(
                    papers_info=papers_info,
                    dimension=dimension,
                )

            try:
                result = self.llm_helper.extract_json(prompt)

                # Build comparison item
                comparison = result.get("comparison", {})
                comparison_matrix.append(ComparisonItem(
                    dimension=dimension,
                    papers=comparison,
                ))

                # Collect similarities and differences
                all_similarities.extend(result.get("similarities", []))
                all_differences.extend(result.get("differences", []))

            except Exception as e:
                print(f"Failed to compare dimension {dimension}: {e}")

        return comparison_matrix, all_similarities, all_differences

    def _build_timeline(self, papers_info: str) -> List[TimelineItem]:
        """Build timeline"""
        prompt = self.TIMELINE_PROMPT.format(papers_info=papers_info)

        try:
            result = self.llm_helper.extract_json(prompt)
            timeline_data = result.get("timeline", [])

            timeline = []
            for item in timeline_data:
                timeline.append(TimelineItem(
                    paper_title=item.get("paper_title", ""),
                    date=item.get("date"),
                    key_contribution=item.get("key_contribution", ""),
                    order=item.get("order", 0),
                ))

            # Sort by order
            timeline.sort(key=lambda x: x.order)
            return timeline

        except Exception as e:
            print(f"Failed to build timeline: {e}")
            return []

    def _analyze_trends(self, papers_info: str) -> Dict[str, Any]:
        """Analyze trends"""
        prompt = self.TREND_PROMPT.format(papers_info=papers_info)

        try:
            result = self.llm_helper.extract_json(prompt)

            # Convert trends to TrendItem objects
            trends_data = result.get("trends", [])
            trends = []
            for item in trends_data:
                trends.append(TrendItem(
                    trend_name=item.get("trend_name", ""),
                    description=item.get("description", ""),
                    evidence=item.get("evidence", []),
                    papers=item.get("papers", []),
                ))

            return {
                "trends": trends,
                "common_themes": result.get("common_themes", []),
                "key_differences": result.get("key_differences", []),
            }

        except Exception as e:
            print(f"Failed to analyze trends: {e}")
            return {"trends": [], "common_themes": [], "key_differences": []}

    def _generate_overall_summary(
        self,
        papers_info: str,
        comparison_matrix: List[ComparisonItem],
        trends: List[TrendItem]
    ) -> str:
        """Generate overall summary"""
        # Prepare comparison summary
        comparison_summary = ""
        for item in comparison_matrix:
            comparison_summary += f"\n{item.dimension}:\n"
            for paper, value in item.papers.items():
                comparison_summary += f"  - {paper}: {value}\n"

        # Prepare trends summary
        trends_summary = ""
        for trend in trends:
            trends_summary += f"\n- {trend.trend_name}: {trend.description}\n"

        # Determine language - force chinese or english only
        language = self.config.report_generator.language.lower()
        if language not in ["chinese", "english"]:
            language = "english"  # Default to english if invalid

        # Map to natural language name
        language_name = "Chinese" if language == "chinese" else "English"

        prompt = self.OVERALL_SUMMARY_PROMPT.format(
            papers_info=papers_info[:3000],  # Limit length
            comparison_summary=comparison_summary[:1500],
            trends_summary=trends_summary[:1000],
            language=language_name,
        )

        return self.llm_helper.ask(prompt)

    def compare_two_papers(self, paper1: PaperAnalysis, paper2: PaperAnalysis) -> Dict[str, Any]:
        """Detailed comparison of two papers"""
        prompt = f"""Perform a detailed comparison of the following two papers:

Paper 1: {paper1.title}
Abstract: {paper1.paper.abstract}
Method: {paper1.technology.method_overview if paper1.technology else 'N/A'}
Innovations: {', '.join(paper1.technology.innovations) if paper1.technology and paper1.technology.innovations else 'N/A'}
Results: {paper1.result.main_results if paper1.result else 'N/A'}

Paper 2: {paper2.title}
Abstract: {paper2.paper.abstract}
Method: {paper2.technology.method_overview if paper2.technology else 'N/A'}
Innovations: {', '.join(paper2.technology.innovations) if paper2.technology and paper2.technology.innovations else 'N/A'}
Results: {paper2.result.main_results if paper2.result else 'N/A'}

Please return results in JSON format:
{{
    "similarities": ["Similarity 1", "Similarity 2", ...],
    "differences": ["Difference 1", "Difference 2", ...],
    "paper1_advantages": ["Advantage 1", ...],
    "paper2_advantages": ["Advantage 1", ...],
    "conclusion": "Overall comparison conclusion"
}}"""

        try:
            return self.llm_helper.extract_json(prompt)
        except Exception as e:
            print(f"Failed to compare papers: {e}")
            return {}


def aggregate_papers(papers: List[PaperAnalysis], config: Optional[Config] = None) -> AggregatedKnowledge:
    """Convenience function: Aggregate papers"""
    aggregator = KnowledgeAggregator(config)
    return aggregator.aggregate(papers)
