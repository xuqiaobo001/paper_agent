"""
Test Configuration
Contains paths and settings for running tests
"""
import os
from pathlib import Path

# Get the root directory of the project
# Current file: paper_agent/test/test_config.py
# Navigate up: test -> paper_agent -> paper_summary (project root)
CURRENT_FILE = Path(__file__).resolve()
TEST_DIR = CURRENT_FILE.parent  # paper_agent/test
PAPER_AGENT_DIR = TEST_DIR.parent  # paper_agent
PROJECT_ROOT = PAPER_AGENT_DIR.parent  # paper_summary

# Test data paths (relative to project root)
TEST_DATA_DIR = PAPER_AGENT_DIR / "origin" / "paper"
TEST_OUTPUT_DIR = TEST_DIR / "output"

# Sample PDF files for testing
SAMPLE_PDF_SINGLE = TEST_DATA_DIR / "DeepSeek-R1.pdf"
SAMPLE_PDF_DIR = TEST_DATA_DIR

# Create output directory if it doesn't exist
TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Test configuration settings
TEST_CONFIG = {
    "pdf_parser": {
        "engine": "pymupdf",
        "extract_images": True,
        "extract_tables": True,
    },
    "test_timeout": 300,  # 5 minutes max for LLM tests
}


def get_test_pdf_path(filename=None):
    """
    Get absolute path to test PDF file

    Args:
        filename: Optional specific PDF filename. If None, returns first available PDF

    Returns:
        Path object to PDF file, or None if not found
    """
    if filename:
        pdf_path = TEST_DATA_DIR / filename
        if pdf_path.exists():
            return pdf_path
        return None

    # Return first PDF found
    if TEST_DATA_DIR.exists():
        pdf_files = list(TEST_DATA_DIR.glob("*.pdf"))
        if pdf_files:
            return pdf_files[0]

    return None


def get_test_output_path(filename):
    """
    Get absolute path for test output file

    Args:
        filename: Output filename

    Returns:
        Path object to output file
    """
    return TEST_OUTPUT_DIR / filename


def check_test_data_available():
    """
    Check if test data directory exists and has PDF files

    Returns:
        bool: True if test data is available
    """
    if not TEST_DATA_DIR.exists():
        return False

    pdf_files = list(TEST_DATA_DIR.glob("*.pdf"))
    return len(pdf_files) > 0


def list_available_test_pdfs():
    """
    List all available test PDF files

    Returns:
        list: List of PDF file paths
    """
    if not TEST_DATA_DIR.exists():
        return []

    return sorted(TEST_DATA_DIR.glob("*.pdf"))


# Print test configuration on import (for debugging)
if __name__ == "__main__":
    print("Test Configuration:")
    print(f"  Project Root: {PROJECT_ROOT}")
    print(f"  Test Data Dir: {TEST_DATA_DIR}")
    print(f"  Test Output Dir: {TEST_OUTPUT_DIR}")
    print(f"  Sample PDF: {SAMPLE_PDF_SINGLE}")
    print(f"  Test data available: {check_test_data_available()}")
    print(f"\nAvailable test PDFs:")
    for pdf in list_available_test_pdfs():
        print(f"    - {pdf.name} ({pdf.stat().st_size / 1024:.1f} KB)")
