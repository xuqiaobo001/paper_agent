"""
PDF Parser Module
Responsible for extracting text content from PDF files
"""
import os
import re
from pathlib import Path
from typing import List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from .models import PaperContent, Figure, Table, Equation, Reference
from .config import Config, get_config


class PDFParser:
    """PDF Parser"""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or get_config()
        self.pdf_config = self.config.pdf_parser

    def parse_all(self, pdf_paths: List[str]) -> List[PaperContent]:
        """Parse all PDFs in parallel"""
        papers = []

        if self.config.parallel.enabled and len(pdf_paths) > 1:
            with ThreadPoolExecutor(max_workers=self.config.parallel.max_workers) as executor:
                futures = {executor.submit(self.parse_single, path): path for path in pdf_paths}
                for future in as_completed(futures):
                    path = futures[future]
                    try:
                        paper = future.result()
                        if paper:
                            papers.append(paper)
                    except Exception as e:
                        print(f"Failed to parse {path}: {e}")
        else:
            for path in pdf_paths:
                try:
                    paper = self.parse_single(path)
                    if paper:
                        papers.append(paper)
                except Exception as e:
                    print(f"Failed to parse {path}: {e}")

        return papers

    def parse_single(self, pdf_path: str) -> Optional[PaperContent]:
        """Parse a single PDF file"""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if self.pdf_config.engine == "pymupdf":
            return self._parse_with_pymupdf(pdf_path)
        elif self.pdf_config.engine == "pdfplumber":
            return self._parse_with_pdfplumber(pdf_path)
        else:
            # Default to pymupdf
            return self._parse_with_pymupdf(pdf_path)

    def _parse_with_pymupdf(self, pdf_path: str) -> PaperContent:
        """Parse PDF using PyMuPDF"""
        try:
            import fitz  # PyMuPDF
        except ImportError:
            raise ImportError("Please install PyMuPDF: pip install PyMuPDF")

        doc = fitz.open(pdf_path)

        # Extract text
        full_text = ""
        max_pages = self.pdf_config.max_pages or len(doc)

        for page_num in range(min(len(doc), max_pages)):
            page = doc[page_num]
            full_text += page.get_text()

        # Extract metadata
        metadata = doc.metadata or {}

        # Extract title
        title = self._extract_title(full_text, metadata)

        # Extract authors
        authors = self._extract_authors(full_text, metadata)

        # Extract abstract
        abstract = self._extract_abstract(full_text)

        # Extract tables
        tables = []
        if self.pdf_config.extract_tables:
            tables = self._extract_tables_pymupdf(doc, max_pages)

        # Extract figures
        figures = []
        if self.pdf_config.extract_images:
            figures = self._extract_figures_pymupdf(doc, max_pages)

        # Extract equations
        equations = self._extract_equations(full_text)

        # Extract references
        references = self._extract_references(full_text)

        doc.close()

        return PaperContent(
            file_path=pdf_path,
            title=title,
            authors=authors,
            abstract=abstract,
            full_text=full_text,
            figures=figures,
            tables=tables,
            equations=equations,
            references=references,
            metadata=metadata,
        )

    def _parse_with_pdfplumber(self, pdf_path: str) -> PaperContent:
        """Parse PDF using pdfplumber"""
        try:
            import pdfplumber
        except ImportError:
            raise ImportError("Please install pdfplumber: pip install pdfplumber")

        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            max_pages = self.pdf_config.max_pages or len(pdf.pages)

            for page_num in range(min(len(pdf.pages), max_pages)):
                page = pdf.pages[page_num]
                text = page.extract_text()
                if text:
                    full_text += text + "\n"

            # Extract title
            title = self._extract_title(full_text, {})

            # Extract authors
            authors = self._extract_authors(full_text, {})

            # Extract abstract
            abstract = self._extract_abstract(full_text)

            # Extract tables
            tables = []
            if self.pdf_config.extract_tables:
                tables = self._extract_tables_pdfplumber(pdf, max_pages)

            # Extract references
            references = self._extract_references(full_text)

        return PaperContent(
            file_path=pdf_path,
            title=title,
            authors=authors,
            abstract=abstract,
            full_text=full_text,
            tables=tables,
            references=references,
        )

    def _extract_title(self, text: str, metadata: dict) -> str:
        """Extract paper title"""
        # Prefer metadata
        if metadata.get("title"):
            return metadata["title"]

        # Extract from beginning of text
        lines = text.strip().split('\n')
        title_lines = []

        for line in lines[:10]:  # Only check first 10 lines
            line = line.strip()
            if not line:
                continue

            # Skip common non-title content
            # Check case-insensitive patterns
            case_insensitive_patterns = [
                r'^(arxiv|preprint|published|accepted|submitted)',
                r'^(abstract|introduction)',
            ]
            # Check case-sensitive patterns
            case_sensitive_patterns = [
                r'^\d{4}',  # Year at beginning
                r'^[a-z]',  # Lowercase letter at beginning usually not title
            ]

            should_skip = False
            for pattern in case_insensitive_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    should_skip = True
                    break

            if not should_skip:
                for pattern in case_sensitive_patterns:
                    if re.match(pattern, line):
                        should_skip = True
                        break

            if should_skip:
                continue

            title_lines.append(line)
            if len(title_lines) >= 2:
                break

        return ' '.join(title_lines) if title_lines else "Untitled"

    def _extract_authors(self, text: str, metadata: dict) -> List[str]:
        """Extract author list"""
        # Prefer metadata
        if metadata.get("author"):
            authors_str = metadata["author"]
            # Try to split authors
            if ',' in authors_str:
                return [a.strip() for a in authors_str.split(',')]
            elif ';' in authors_str:
                return [a.strip() for a in authors_str.split(';')]
            return [authors_str]

        # Extract from text (simplified implementation)
        return []

    def _extract_abstract(self, text: str) -> str:
        """Extract abstract"""
        # Find Abstract section
        patterns = [
            r'Abstract[:\s]*\n(.*?)(?=\n\s*(?:1\.?\s*)?Introduction|\n\s*Keywords|\n\s*\d+\s)',
            r'ABSTRACT[:\s]*\n(.*?)(?=\n\s*(?:1\.?\s*)?INTRODUCTION|\n\s*KEYWORDS|\n\s*\d+\s)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                abstract = match.group(1).strip()
                # Clean extra whitespace
                abstract = re.sub(r'\s+', ' ', abstract)
                return abstract

        return ""

    def _extract_references(self, text: str) -> List[Reference]:
        """Extract references"""
        references = []

        # Find References section
        ref_patterns = [
            r'References?\s*\n(.*?)$',
            r'REFERENCES?\s*\n(.*?)$',
        ]

        ref_section = ""
        for pattern in ref_patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                ref_section = match.group(1)
                break

        if not ref_section:
            return references

        # Parse reference entries
        # Match [1], [2] or 1., 2. format
        entries = re.split(r'\n\s*\[(\d+)\]|\n\s*(\d+)\.\s+', ref_section)

        idx = 1
        for entry in entries:
            if entry and not entry.isdigit():
                entry = entry.strip()
                if len(entry) > 10:  # Filter too short content
                    references.append(Reference(
                        index=idx,
                        text=entry,
                    ))
                    idx += 1

        return references

    def _extract_tables_pymupdf(self, doc, max_pages: int) -> List[Table]:
        """Extract tables using PyMuPDF"""
        tables = []
        for page_num in range(min(len(doc), max_pages)):
            page = doc[page_num]
            # PyMuPDF table extraction
            try:
                page_tables = page.find_tables()
                for table_obj in page_tables:
                    table_data = table_obj.extract()
                    content_str = str(table_data)

                    # Check if table extraction is incomplete (only header, <= 1 row)
                    is_incomplete = len(table_data) <= 1

                    image_data = None
                    if is_incomplete:
                        # Extract table as screenshot
                        image_data = self._screenshot_table(page, table_obj)

                    tables.append(Table(
                        page=page_num + 1,
                        content=content_str,
                        image_data=image_data,
                    ))
            except Exception:
                pass
        return tables

    def _screenshot_table(self, page, table_obj) -> Optional[bytes]:
        """
        Screenshot a table region as PNG image

        Args:
            page: PyMuPDF page object
            table_obj: PyMuPDF table object

        Returns:
            PNG image bytes, or None if failed
        """
        try:
            import fitz

            # Get table bounding box
            table_rect = fitz.Rect(table_obj.bbox)

            # Find actual table extent by analyzing text positions
            text_instances = page.get_text("words")

            # Find table start (header)
            table_y0 = table_rect.y0
            table_y1 = table_rect.y1

            # Find text blocks in table region to determine actual height
            table_words = []
            for word_data in text_instances:
                x0, y0, x1, y1, word = word_data[:5]

                # Check if word is in table's horizontal range
                if (x0 >= table_rect.x0 - 20 and x0 <= table_rect.x1 + 20 and
                    y0 >= table_y0 - 10):
                    table_words.append((y0, y1, word))

            # Sort by y position and find extent
            if table_words:
                table_words.sort(key=lambda w: w[0])

                # Find where table ends: look for large gap or next section
                last_y = table_words[0][1]
                for y0, y1, word in table_words[1:]:
                    gap = y0 - last_y

                    # Stop at large gap or section markers
                    if gap > 30 or word.lower() in ['table', 'figure', 'section']:
                        break

                    table_y1 = y1
                    last_y = y1

            # Create extended rectangle
            rect = fitz.Rect(
                table_rect.x0 - 5,
                table_y0 - 5,
                table_rect.x1 + 5,
                table_y1 + 5
            )

            # Render as image (DPI=200 for good quality)
            pix = page.get_pixmap(clip=rect, dpi=200)

            # Convert to PNG bytes
            return pix.tobytes("png")

        except Exception as e:
            print(f"Failed to screenshot table: {e}")
            return None

    def _extract_tables_pdfplumber(self, pdf, max_pages: int) -> List[Table]:
        """Extract tables using pdfplumber"""
        tables = []
        for page_num in range(min(len(pdf.pages), max_pages)):
            page = pdf.pages[page_num]
            page_tables = page.extract_tables()
            for table in page_tables:
                tables.append(Table(
                    page=page_num + 1,
                    content=str(table),
                ))
        return tables

    def _extract_figures_pymupdf(self, doc, max_pages: int) -> List[Figure]:
        """Extract figures using PyMuPDF"""
        import fitz
        figures = []

        for page_num in range(min(len(doc), max_pages)):
            page = doc[page_num]
            image_list = page.get_images()

            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]  # Image reference number
                    base_image = doc.extract_image(xref)
                    image_data = base_image["image"]  # Binary image data
                    image_ext = base_image["ext"]      # Image extension (png, jpg, etc.)

                    # Try to extract caption from nearby text
                    caption = self._extract_figure_caption(page, page_num, img_index)

                    figures.append(Figure(
                        page=page_num + 1,
                        caption=caption,
                        image_data=image_data,
                    ))
                except Exception as e:
                    # If extraction fails, create placeholder
                    figures.append(Figure(
                        page=page_num + 1,
                        caption=f"Figure {len(figures) + 1} (page {page_num + 1})",
                    ))
        return figures

    def _extract_figure_caption(self, page, page_num: int, img_index: int) -> str:
        """Extract figure caption from page text"""
        text = page.get_text()

        # Look for common figure caption patterns
        patterns = [
            rf'Figure\s+{img_index + 1}[:\.\s]+(.*?)(?=\n\n|\nTable|\nFigure\s+\d+|$)',
            rf'Fig\.\s+{img_index + 1}[:\.\s]+(.*?)(?=\n\n|\nTable|\nFig\.\s+\d+|$)',
            rf'图\s+{img_index + 1}[:\.\s]+(.*?)(?=\n\n|\n表|\n图\s+\d+|$)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                caption = match.group(1).strip()
                # Clean up and limit length
                caption = re.sub(r'\s+', ' ', caption)
                if len(caption) > 200:
                    caption = caption[:197] + "..."
                return f"Figure {img_index + 1}: {caption}"

        return f"Figure {img_index + 1} (page {page_num + 1})"

    def _is_likely_equation(self, text: str) -> bool:
        """
        Check if text is likely a mathematical equation rather than regular prose

        Args:
            text: Text to validate

        Returns:
            True if text appears to be a mathematical equation
        """
        # Filter out obvious prose first
        words = text.split()

        # Check for common English words (prose indicator)
        common_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                       'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
                       'could', 'may', 'might', 'must', 'can', 'of', 'in', 'on', 'at', 'to',
                       'for', 'with', 'by', 'from', 'as', 'and', 'or', 'but', 'if', 'when',
                       'where', 'why', 'how', 'which', 'that', 'this', 'these', 'those',
                       'demonstrating', 'introduced', 'tasks', 'exceptional', 'proficiency',
                       'achieving', 'performance', 'results', 'shows', 'across', 'compared'}

        if len(words) > 5:
            common_word_count = sum(1 for word in words if word.lower() in common_words)
            # If more than 50% are common English words, definitely not an equation
            if common_word_count / len(words) > 0.5:
                return False

        # Check for mathematical indicators
        math_indicators = [
            r'[=+*/^](?!\w)',        # Operators not followed by word char (to exclude file names, etc.)
            r'\\[a-zA-Z]+\{',        # LaTeX commands with braces like \sum{, \frac{
            r'[α-ωΑ-Ω]',             # Greek letters
            r'\b\d+\.\d+\b',         # Decimal numbers
            r'\b[a-z]_\{[^}]+\}',    # Subscripts like x_{i}
            r'\^\{[^}]+\}',          # Superscripts like x^{2}
            r'\\frac|\\sum|\\int|\\prod|\\log|\\exp',  # Common math functions
            r'∈|∉|⊂|⊆|∪|∩|≤|≥|≠',   # Mathematical symbols
            r'\b[a-zA-Z]\s*[=]\s*',  # Variable assignment like "x = "
        ]

        # Count mathematical indicators
        math_score = sum(1 for pattern in math_indicators if re.search(pattern, text))

        # If no mathematical indicators, not an equation
        if math_score == 0:
            return False

        # If has strong mathematical indicators, likely an equation
        return True

    def _extract_equations(self, text: str) -> List[Equation]:
        """Extract equations from text

        Looks for LaTeX-style equations and numbered equations
        """
        equations = []

        # Pattern 1: LaTeX inline equations: $...$
        inline_pattern = r'\$([^\$]+)\$'

        # Pattern 2: LaTeX display equations: $$...$$
        display_pattern = r'\$\$(.+?)\$\$'

        # Pattern 3: LaTeX environments: \begin{equation}...\end{equation}
        env_pattern = r'\\begin\{(?:equation|align|eqnarray)\*?\}(.+?)\\end\{(?:equation|align|eqnarray)\*?\}'

        # Pattern 4: Numbered equations in text like (1), (2), etc.
        # with context before and after
        numbered_pattern = r'([A-Za-z\s=+\-*/0-9\(\)\[\]]+)\s*\((\d+)\)'

        page_num = 1  # Simplified, in real usage would track pages

        # Extract display equations (highest priority)
        for match in re.finditer(display_pattern, text, re.DOTALL):
            eq_text = match.group(1).strip()
            if len(eq_text) > 3 and self._is_likely_equation(eq_text):  # Validate equation
                equations.append(Equation(
                    page=page_num,
                    equation_text=eq_text,
                    caption=f"Display equation"
                ))

        # Extract LaTeX environment equations
        for match in re.finditer(env_pattern, text, re.DOTALL | re.IGNORECASE):
            eq_text = match.group(1).strip()
            if len(eq_text) > 3:
                # Try to find equation number
                eq_num_match = re.search(r'\\label\{([^}]+)\}', eq_text)
                eq_num = eq_num_match.group(1) if eq_num_match else None

                equations.append(Equation(
                    page=page_num,
                    equation_text=eq_text,
                    equation_number=eq_num,
                    caption=f"LaTeX equation"
                ))

        # If no LaTeX equations found, look for numbered expressions
        if not equations:
            # Look for patterns like "x = y + z  (1)"
            for match in re.finditer(numbered_pattern, text):
                expr = match.group(1).strip()
                eq_num = match.group(2)

                # Check if it looks like a mathematical expression
                # Use the same validation as display equations
                if len(expr) > 10 and self._is_likely_equation(expr):
                    equations.append(Equation(
                        page=page_num,
                        equation_text=expr,
                        equation_number=f"({eq_num})",
                        caption=f"Equation {eq_num}"
                    ))

        return equations


def parse_pdfs(pdf_paths: List[str], config: Optional[Config] = None) -> List[PaperContent]:
    """Convenience function: Parse multiple PDFs"""
    parser = PDFParser(config)
    return parser.parse_all(pdf_paths)


def parse_pdf(pdf_path: str, config: Optional[Config] = None) -> Optional[PaperContent]:
    """Convenience function: Parse single PDF"""
    parser = PDFParser(config)
    return parser.parse_single(pdf_path)
