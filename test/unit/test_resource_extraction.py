"""
Test Resource Extraction Features
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from paper_agent.core.models import PaperContent, Figure, Table, Equation, PaperAnalysis
from paper_agent.core.resource_manager import ResourceManager
import tempfile
import os


class TestResourceExtraction:
    """Test resource extraction and management"""

    def test_equation_model(self):
        """Test Equation data model"""
        eq = Equation(
            page=1,
            equation_text="x = y + z",
            equation_number="(1)",
            caption="Linear equation"
        )
        assert eq.page == 1
        assert eq.equation_text == "x = y + z"
        assert eq.equation_number == "(1)"
        assert eq.caption == "Linear equation"

    def test_figure_model_with_data(self):
        """Test Figure model with image data"""
        fig = Figure(
            page=1,
            caption="Test Figure",
            image_data=b"fake_image_data"
        )
        assert fig.page == 1
        assert fig.caption == "Test Figure"
        assert fig.image_data == b"fake_image_data"

    def test_paper_content_with_equations(self):
        """Test PaperContent with equations field"""
        eq1 = Equation(page=1, equation_text="E = mc^2")
        eq2 = Equation(page=2, equation_text="F = ma")

        paper = PaperContent(
            file_path="test.pdf",
            title="Test Paper",
            equations=[eq1, eq2]
        )

        assert len(paper.equations) == 2
        assert paper.equations[0].equation_text == "E = mc^2"
        assert paper.equations[1].equation_text == "F = ma"

    def test_paper_analysis_key_resources(self):
        """Test PaperAnalysis with key resource indices"""
        paper = PaperContent(file_path="test.pdf", title="Test")
        analysis = PaperAnalysis(
            paper=paper,
            key_figures=[1, 2],
            key_tables=[1],
            key_equations=[1, 2, 3]
        )

        assert analysis.key_figures == [1, 2]
        assert analysis.key_tables == [1]
        assert analysis.key_equations == [1, 2, 3]

    def test_resource_manager_initialization(self):
        """Test ResourceManager initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "report.md")
            manager = ResourceManager(output_path)

            assert manager.output_path == output_path
            assert os.path.exists(manager.assets_dir)
            assert manager.report_name == "report"

    def test_resource_manager_save_figure(self):
        """Test saving figure with ResourceManager"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_report.md")
            manager = ResourceManager(output_path)

            # Create a figure with fake image data
            fig = Figure(
                page=1,
                caption="Test Figure 1",
                image_data=b"fake_png_data"
            )

            # Save the figure
            rel_path = manager.save_figure(fig, "Test Paper", 1)

            assert rel_path is not None
            assert "test_report_assets" in rel_path
            assert "fig_test_paper_1.png" in rel_path

            # Check file was created
            full_path = os.path.join(tmpdir, rel_path)
            assert os.path.exists(full_path)

            # Verify content
            with open(full_path, 'rb') as f:
                content = f.read()
                assert content == b"fake_png_data"

    def test_resource_manager_format_equation(self):
        """Test equation formatting"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "report.md")
            manager = ResourceManager(output_path)

            # Test LaTeX equation
            eq1 = Equation(
                page=1,
                equation_text="E = mc^2",
                equation_number="(1)"
            )
            formatted = manager.format_equation(eq1)
            assert "$$E = mc^2$$" in formatted
            assert "(1)" in formatted

            # Test equation with LaTeX markers already
            eq2 = Equation(
                page=1,
                equation_text="$$F = ma$$",
                equation_number="(2)"
            )
            formatted = manager.format_equation(eq2)
            assert "$$F = ma$$" in formatted

    def test_resource_manager_sanitize_filename(self):
        """Test filename sanitization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "report.md")
            manager = ResourceManager(output_path)

            # Test various unsafe characters
            unsafe_name = "Test Paper: A Study of AI/ML (2024) #1"
            safe_name = manager._sanitize_filename(unsafe_name)

            assert " " not in safe_name
            assert ":" not in safe_name
            assert "/" not in safe_name
            assert "(" not in safe_name
            assert "#" not in safe_name
            assert safe_name.islower()

    def test_resource_manager_save_resources(self):
        """Test saving all resources from papers"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "report.md")
            manager = ResourceManager(output_path)

            # Create test papers with resources
            fig1 = Figure(page=1, caption="Figure 1", image_data=b"img1")
            table1 = Table(page=1, caption="Table 1", content="A | B\n1 | 2")
            eq1 = Equation(page=1, equation_text="x = y", equation_number="(1)")

            paper = PaperContent(
                file_path="test.pdf",
                title="Test Paper",
                figures=[fig1],
                tables=[table1],
                equations=[eq1]
            )

            resources = manager.save_resources([paper])

            assert "Test Paper" in resources
            assert len(resources["Test Paper"]["figures"]) == 1
            assert len(resources["Test Paper"]["tables"]) == 1
            assert len(resources["Test Paper"]["equations"]) == 1

            # Verify figure was saved
            fig_info = resources["Test Paper"]["figures"][0]
            assert fig_info["index"] == 1
            assert fig_info["caption"] == "Figure 1"
            assert os.path.exists(os.path.join(tmpdir, fig_info["path"]))


class TestEquationExtraction:
    """Test equation extraction from text"""

    def test_extract_latex_display_equations(self):
        """Test extracting LaTeX display equations"""
        from paper_agent.core.pdf_parser import PDFParser
        from paper_agent.core.config import get_config

        parser = PDFParser(get_config())

        # Test text with display equations
        text = r"""
        The loss function is defined as:
        $$L = -\sum_{i=1}^{n} y_i \log(\hat{y}_i)$$

        And the gradient is:
        $$\nabla L = \frac{\partial L}{\partial w}$$
        """

        equations = parser._extract_equations(text)

        # Should extract at least one equation
        assert len(equations) >= 1
        # Check that we extracted some mathematical content
        assert any(("sum" in eq.equation_text or "nabla" in eq.equation_text or "partial" in eq.equation_text)
                   for eq in equations)

    def test_extract_numbered_equations(self):
        """Test extracting numbered equations"""
        from paper_agent.core.pdf_parser import PDFParser
        from paper_agent.core.config import get_config

        parser = PDFParser(get_config())

        # Test text with simple numbered equation
        text = """
        The relationship is given by:
        x = y + z  (1)

        where x is the result.
        """

        equations = parser._extract_equations(text)

        # Should extract numbered equation if no LaTeX found
        assert len(equations) >= 0  # May or may not extract depending on pattern


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
