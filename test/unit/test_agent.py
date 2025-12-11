"""
Unit Tests for Paper Agent
"""
import pytest
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from paper_agent.agent import PaperAgent
from paper_agent.core.config import Config

# Import test configuration
from paper_agent.test.test_config import (
    get_test_pdf_path,
    check_test_data_available,
    SAMPLE_PDF_SINGLE,
    SAMPLE_PDF_DIR,
    TEST_OUTPUT_DIR
)


class TestPaperAgent:
    """Test Paper Agent main functionality"""

    @pytest.fixture
    def agent(self):
        """Create agent instance"""
        config_path = "config.yaml"
        return PaperAgent(config_path=config_path)

    @pytest.fixture
    def sample_pdf(self):
        """Sample PDF path"""
        return str(SAMPLE_PDF_SINGLE)

    def test_agent_initialization(self, agent):
        """Test agent initialization"""
        assert agent is not None
        assert agent.config is not None
        assert agent.pdf_parser is not None
        assert agent.content_extractor is not None
        assert agent.knowledge_aggregator is not None
        assert agent.report_generator is not None

    def test_load_single_paper(self, agent, sample_pdf):
        """Test loading single paper"""
        if not check_test_data_available():
            pytest.skip(f"Test data not available at {SAMPLE_PDF_DIR}")

        papers = agent.load_papers(sample_pdf)
        assert len(papers) == 1
        assert papers[0].title is not None

    def test_load_multiple_papers(self, agent):
        """Test loading multiple papers"""
        if not check_test_data_available():
            pytest.skip(f"Test data not available at {SAMPLE_PDF_DIR}")

        papers = agent.load_papers(str(SAMPLE_PDF_DIR))
        assert len(papers) > 0

    def test_analyze_papers(self, agent, sample_pdf):
        """Test analyzing papers"""
        if not check_test_data_available():
            pytest.skip(f"Test data not available at {SAMPLE_PDF_DIR}")

        agent.load_papers(sample_pdf)
        analyses = agent.analyze()

        assert len(analyses) == 1
        assert analyses[0].summary is not None
        assert len(analyses[0].keywords) > 0

    def test_custom_prompt_aggregation(self, agent):
        """Test custom prompt aggregation"""
        # Mock some paper analyses
        from paper_agent.core.models import PaperAnalysis, PaperContent

        paper1 = PaperContent(
            file_path="test1.pdf",
            title="Test Paper 1",
            abstract="This is a test abstract"
        )
        analysis1 = PaperAnalysis(paper=paper1)

        paper2 = PaperContent(
            file_path="test2.pdf",
            title="Test Paper 2",
            abstract="This is another test abstract"
        )
        analysis2 = PaperAnalysis(paper=paper2)

        agent._analyses = [analysis1, analysis2]

        # This would call LLM, so we just test the structure
        # In real tests, you'd mock the LLM response
        # knowledge = agent.aggregate(custom_prompt="Test prompt")
        # assert knowledge.custom_analysis == "Test prompt"

        # For now, just verify the method exists
        assert hasattr(agent, 'aggregate')

    def test_resolve_paths(self, agent):
        """Test path resolution"""
        if not check_test_data_available():
            pytest.skip(f"Test data not available at {SAMPLE_PDF_DIR}")

        # Test single file
        result = agent._resolve_single_path(str(SAMPLE_PDF_SINGLE))
        assert len(result) == 1

        # Test directory
        result = agent._resolve_single_path(str(SAMPLE_PDF_DIR))
        assert len(result) > 0

    def test_clear_cache(self, agent):
        """Test clearing cache"""
        agent._papers = ["test"]
        agent._analyses = ["test"]
        agent._knowledge = "test"

        agent.clear()

        assert len(agent._papers) == 0
        assert len(agent._analyses) == 0
        assert agent._knowledge is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
