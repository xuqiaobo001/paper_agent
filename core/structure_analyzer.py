"""
Structure Analyzer Module
Responsible for identifying paper section structure
"""
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from .models import PaperContent
from .config import Config, get_config


@dataclass
class Section:
    """Section information"""
    section_type: str
    title: str
    content: str
    start_pos: int
    end_pos: int
    level: int = 1  # Section level: 1=first-level, 2=second-level


class StructureAnalyzer:
    """Structure Analyzer"""

    # Default section patterns
    DEFAULT_SECTION_PATTERNS = {
        "abstract": [
            r"^abstract\s*$",
        ],
        "introduction": [
            r"^(?:\d+\.?\s*)?introduction\s*$",
            r"^1\s+introduction",
        ],
        "related_work": [
            r"^(?:\d+\.?\s*)?related\s+work\s*$",
            r"^(?:\d+\.?\s*)?background\s*$",
            r"^(?:\d+\.?\s*)?preliminaries?\s*$",
        ],
        "method": [
            r"^(?:\d+\.?\s*)?method(?:ology|s)?\s*$",
            r"^(?:\d+\.?\s*)?approach\s*$",
            r"^(?:\d+\.?\s*)?(?:our\s+)?model\s*$",
            r"^(?:\d+\.?\s*)?proposed\s+method\s*$",
            r"^(?:\d+\.?\s*)?framework\s*$",
            r"^(?:\d+\.?\s*)?architecture\s*$",
        ],
        "experiment": [
            r"^(?:\d+\.?\s*)?experiments?\s*$",
            r"^(?:\d+\.?\s*)?evaluation\s*$",
            r"^(?:\d+\.?\s*)?experimental\s+(?:setup|results?)\s*$",
        ],
        "result": [
            r"^(?:\d+\.?\s*)?results?\s*$",
            r"^(?:\d+\.?\s*)?findings?\s*$",
        ],
        "discussion": [
            r"^(?:\d+\.?\s*)?discussion\s*$",
            r"^(?:\d+\.?\s*)?analysis\s*$",
        ],
        "conclusion": [
            r"^(?:\d+\.?\s*)?conclusions?\s*$",
            r"^(?:\d+\.?\s*)?summary\s*$",
            r"^(?:\d+\.?\s*)?concluding\s+remarks?\s*$",
        ],
        "references": [
            r"^references?\s*$",
            r"^bibliography\s*$",
        ],
        "appendix": [
            r"^(?:appendix|appendices)\s*",
        ],
    }

    def __init__(self, config: Optional[Config] = None):
        self.config = config or get_config()
        self.section_patterns = self._load_patterns()

    def _load_patterns(self) -> Dict[str, List[str]]:
        """Load section patterns"""
        # Prefer patterns from config file
        config_patterns = self.config.structure_analyzer.section_patterns
        if config_patterns:
            # Merge config and default patterns
            patterns = self.DEFAULT_SECTION_PATTERNS.copy()
            for section_type, pattern_list in config_patterns.items():
                if section_type in patterns:
                    patterns[section_type].extend(pattern_list)
                else:
                    patterns[section_type] = pattern_list
            return patterns
        return self.DEFAULT_SECTION_PATTERNS

    def analyze(self, paper: PaperContent) -> Dict[str, str]:
        """Analyze paper structure and extract section content"""
        text = paper.full_text
        sections = self._find_sections(text)

        # Extract section content
        result = {}
        for section in sections:
            if section.section_type not in result:
                result[section.section_type] = section.content
            else:
                # Merge same type sections
                result[section.section_type] += "\n\n" + section.content

        # Ensure abstract exists
        if "abstract" not in result and paper.abstract:
            result["abstract"] = paper.abstract

        return result

    def _find_sections(self, text: str) -> List[Section]:
        """Find all sections in text"""
        sections = []
        lines = text.split('\n')

        # Record all found section title positions
        section_positions = []

        current_pos = 0
        for line_num, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped:
                current_pos += len(line) + 1
                continue

            # Check if line is a section title
            section_type = self._identify_section(line_stripped)
            if section_type:
                section_positions.append({
                    "type": section_type,
                    "title": line_stripped,
                    "line_num": line_num,
                    "pos": current_pos,
                    "level": self._get_section_level(line_stripped),
                })

            current_pos += len(line) + 1

        # Extract section content
        for i, sec_info in enumerate(section_positions):
            start_line = sec_info["line_num"] + 1  # Skip title line
            end_line = section_positions[i + 1]["line_num"] if i + 1 < len(section_positions) else len(lines)

            content = '\n'.join(lines[start_line:end_line]).strip()

            sections.append(Section(
                section_type=sec_info["type"],
                title=sec_info["title"],
                content=content,
                start_pos=sec_info["pos"],
                end_pos=sec_info["pos"] + len(content),
                level=sec_info["level"],
            ))

        return sections

    def _identify_section(self, line: str) -> Optional[str]:
        """Identify if line is a section title"""
        line_lower = line.lower().strip()

        # Remove common numbering formats
        line_clean = re.sub(r'^[\d.]+\s*', '', line_lower)

        for section_type, patterns in self.section_patterns.items():
            for pattern in patterns:
                if re.match(pattern, line_clean, re.IGNORECASE):
                    return section_type
                if re.match(pattern, line_lower, re.IGNORECASE):
                    return section_type

        return None

    def _get_section_level(self, line: str) -> int:
        """Determine section level"""
        # Simple logic: first-level numbering = level 1, second-level = level 2
        if re.match(r'^\d+\s+', line):
            return 1
        if re.match(r'^\d+\.\d+\s+', line):
            return 2
        if re.match(r'^\d+\.\d+\.\d+\s+', line):
            return 3
        return 1

    def get_section_summary(self, paper: PaperContent) -> Dict[str, Dict]:
        """Get section summary information"""
        sections = self.analyze(paper)
        summary = {}

        for section_type, content in sections.items():
            summary[section_type] = {
                "length": len(content),
                "word_count": len(content.split()),
                "preview": content[:200] + "..." if len(content) > 200 else content,
            }

        return summary


class SectionExtractor:
    """Section Content Extractor"""

    def __init__(self, analyzer: Optional[StructureAnalyzer] = None):
        self.analyzer = analyzer or StructureAnalyzer()

    def extract_section(self, paper: PaperContent, section_type: str) -> str:
        """Extract specified section content"""
        sections = self.analyzer.analyze(paper)
        return sections.get(section_type, "")

    def extract_multiple_sections(self, paper: PaperContent, section_types: List[str]) -> Dict[str, str]:
        """Extract multiple section content"""
        sections = self.analyzer.analyze(paper)
        return {st: sections.get(st, "") for st in section_types}

    def get_main_content(self, paper: PaperContent) -> str:
        """Get main content (excluding references and appendix)"""
        sections = self.analyzer.analyze(paper)

        exclude_types = {"references", "appendix"}
        main_content_parts = []

        for section_type, content in sections.items():
            if section_type not in exclude_types:
                main_content_parts.append(content)

        return "\n\n".join(main_content_parts)


def analyze_structure(paper: PaperContent, config: Optional[Config] = None) -> Dict[str, str]:
    """Convenience function: Analyze paper structure"""
    analyzer = StructureAnalyzer(config)
    return analyzer.analyze(paper)
