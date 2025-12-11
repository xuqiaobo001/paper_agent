# Paper Reading Agent

An intelligent paper analysis tool powered by LLM. It can automatically parse academic papers, extract key information from multiple dimensions, and generate structured reading reports.

## Features

- **🎯 Custom Analysis Prompts** ⭐ NEW: Define your own analysis requirements with natural language (e.g., "compare technical approaches", "analyze data processing methods")
- **📊 Key Resource Extraction** ⭐ NEW: Automatically identifies and extracts key figures, tables, and equations from papers
  - Intelligent selection of most important visual elements using LLM
  - Saves figures as images in assets directory
  - **🖼️ Smart Table Screenshot** ⭐ ENHANCED: Automatically captures complete tables as high-quality images when text extraction fails
  - Embeds key tables and equations in the report
  - All resources referenced in markdown format
- **📝 Improved Title Extraction**: Enhanced paper title detection with better pattern matching for various PDF layouts
- **Automatic PDF Parsing**: Extract text, tables, figures, and references from academic papers
- **Four-Dimension Analysis**: Analyze papers from background, technology, experiment, and result perspectives
- **Multi-Paper Comparison**: Support horizontal comparison and trend analysis of multiple papers
- **Flexible Configuration**: Support multiple LLM providers (OpenAI, Anthropic, DeepSeek, Zhipu, Ollama, Azure, Custom)
- **Parallel Processing**: Multi-threaded analysis for faster processing
- **Multiple Output Formats**: Support Markdown, JSON, HTML output formats

> **⚠️ Important**: Please review [Limitations and Constraints](#limitations-and-constraints) before use to understand supported scenarios and potential issues.

## 🆕 Recent Updates

### v1.1.0 - Enhanced Table Handling & Bug Fixes

**🖼️ Smart Table Screenshot**
- **Automatic fallback to screenshots**: When text extraction fails to capture complete table data, the tool now automatically captures high-quality screenshots (200 DPI)
- **Intelligent boundary detection**: Analyzes text positions to find the complete extent of tables, ensuring all rows are captured
- **Seamless integration**: Tables are displayed as images in reports when necessary, preserving exact visual appearance

**🐛 Bug Fixes**
- **Fixed title extraction bug**: Resolved "Untitled" issue caused by overly aggressive pattern matching
- **Fixed max_tokens configuration**: Corrected default value to respect API limits (32768 instead of 655536)
- **Improved table formatting**: Tables that can be extracted as text are now properly formatted as Markdown tables

**Why These Updates Matter:**
- Many academic papers (especially from arXiv) use complex table layouts that traditional text extraction cannot handle
- The tool now ensures you never miss important tabular data in your analysis
- More reliable paper metadata extraction means better organized reports

## 🎯 What's New: Custom Analysis Prompts

The custom analysis feature allows you to define your own analysis requirements using natural language, giving you precise control over what aspects of the papers you want to focus on.

### Why Use Custom Analysis?

**Default Mode** provides comprehensive structured analysis with comparison matrices, timelines, and trends - great for general understanding.

**Custom Mode** gives you targeted, focused analysis - perfect when you need to:
- Compare specific technical aspects (e.g., "training efficiency")
- Evaluate particular dimensions (e.g., "data quality and preprocessing")
- Get insights on specialized topics (e.g., "deployment considerations")
- Answer specific research questions (e.g., "which approach scales better?")

### Quick Example

```bash
# Default mode: Comprehensive structured comparison
paper-agent analyze paper1.pdf paper2.pdf -t comparison

# Custom mode: Focus on what you care about
paper-agent analyze paper1.pdf paper2.pdf -t comparison \
  -p "compare the training methods and identify which is more computationally efficient"
```

### Use Cases

| Scenario | Custom Prompt Example |
|----------|----------------------|
| Method Comparison | "compare the technical approaches and their computational complexity" |
| Data Analysis | "analyze data processing pipelines and data quality control methods" |
| Performance Evaluation | "evaluate performance improvements and identify the key contributing factors" |
| Architecture Study | "compare model architectures and their scalability characteristics" |
| Practical Assessment | "assess practical applicability for production deployment" |
| Innovation Analysis | "identify the most significant innovations and their potential impact" |

## 📊 Key Resource Extraction

The tool now automatically identifies and extracts the most important visual elements from papers:

### How It Works

1. **Automatic Extraction**: During PDF parsing, the tool extracts:
   - Figures with captions (stored as PNG images)
   - Tables with content
   - Mathematical equations (LaTeX format)

2. **Intelligent Selection**: LLM analyzes the paper and selects:
   - Up to 3 most important figures
   - Up to 3 most important tables
   - Up to 5 key equations

3. **Report Integration**: Selected resources are:
   - Saved to `{report_name}_assets/` directory
   - Referenced in markdown with proper paths
   - Displayed in a "Key Resources" section at the end of the report

### 🖼️ Smart Table Screenshot (Enhanced)

When PDF table extraction fails to capture complete table data (common with complex layouts), the tool **automatically captures high-quality screenshots**:

**How It Works:**
1. **Detection**: Detects when text extraction only captures headers (≤1 row)
2. **Intelligent Boundary Detection**: Analyzes text positions to find complete table extent
3. **High-Quality Capture**: Screenshots table at 200 DPI for clarity
4. **Seamless Integration**: Displays as image in report instead of incomplete text

**Why This Matters:**
- Many academic papers use complex table layouts that resist text extraction
- Text-based tables may have merged cells, multi-line headers, or special formatting
- Screenshots preserve the original visual presentation exactly as published

**Example Output:**

```markdown
#### Key Tables

**Table 3: Performance Comparison**

![Table 3: Performance Comparison](report_assets/table_paper_1.png)
```

**Note:** Tables that extract successfully are still rendered as Markdown tables for better searchability.

### Example Output

```markdown
## Key Resources

### Paper Title

#### Key Figures

**Figure 1: Model Architecture**

![Figure 1: Model Architecture](report_summary_assets/fig_paper_title_1.png)

#### Key Tables

**Table 1: Performance Comparison**

| Model | Accuracy | Speed |
|-------|----------|-------|
| ...   | ...      | ...   |

#### Key Equations

$$Loss = -\sum_{i=1}^{n} y_i \log(\hat{y}_i)$$   &nbsp;&nbsp;&nbsp;&nbsp; (1)
```

### Configuration

Enable image extraction in your config:

```yaml
pdf_parser:
  extract_images: true  # Default: true
  extract_tables: true
```

## Installation

```bash
# Install from source
cd paper_agent
pip install -e .

# Or install dependencies directly
pip install -r requirements.txt
```

## Quick Start

### 1. Initialize Configuration

```bash
# Generate default configuration file
paper-agent init -o config.yaml
```

Edit `config.yaml` to set your LLM API key:

```yaml
llm:
  provider: "openai"
  model: "gpt-4o"
  api_key: "${OPENAI_API_KEY}"  # Or set directly
```

### 2. Analyze Papers

```bash
# Analyze single paper
paper-agent analyze paper.pdf --type single -o summary.md

# Compare multiple papers (default mode)
paper-agent analyze paper1.pdf paper2.pdf --type comparison -o compare.md

# 🎯 NEW: Custom analysis with your own requirements
paper-agent analyze paper1.pdf paper2.pdf --type comparison \
  --prompt "compare technical approaches and identify key differences"

# More custom analysis examples
paper-agent analyze paper1.pdf paper2.pdf --type comparison \
  --prompt "analyze data processing methods and their advantages"

paper-agent analyze paper1.pdf paper2.pdf --type comparison \
  --prompt "focus on architectural innovations and practical applications"

# Analyze technology trends
paper-agent analyze ./papers/ --type trend -o trend_report.md
```

## CLI Usage

```bash
paper-agent analyze [OPTIONS] INPUT...

Arguments:
  INPUT                    Input PDF file paths (can specify multiple, or directory)

Options:
  -t, --type TYPE          Report type: single/comparison/trend (default: single)
  -o, --output PATH        Output file path
  --title TEXT             Report title
  -p, --prompt TEXT        🎯 Custom analysis requirement (e.g., "analyze technical differences")
  -c, --config PATH        Configuration file path
  -f, --format FORMAT      Output format: markdown/json/html (default: markdown)
  -v, --verbose            Show verbose output
```

### Examples

```bash
# Single paper summary
paper-agent analyze paper.pdf

# Compare two papers (default mode - structured comparison matrix)
paper-agent analyze paper1.pdf paper2.pdf -t comparison

# 🎯 Custom analysis examples
# Focus on specific aspects with natural language prompts
paper-agent analyze paper1.pdf paper2.pdf -t comparison \
  -p "compare the training methods and identify which is more efficient"

paper-agent analyze paper1.pdf paper2.pdf -t comparison \
  -p "analyze the experimental design and data quality"

paper-agent analyze paper1.pdf paper2.pdf -t comparison \
  -p "evaluate the practical applicability and deployment considerations"

# Analyze all papers in directory
paper-agent analyze ./papers/ -t trend -o trend_analysis.md

# Use custom configuration
paper-agent analyze paper.pdf -c my_config.yaml

# Output as HTML
paper-agent analyze paper.pdf -f html -o report.html
```

## Python API

```python
from paper_agent import PaperAgent

# Create agent
agent = PaperAgent(config_path="config.yaml")

# One-click analysis
report = agent.run(
    input_path="paper.pdf",
    report_type="single",
    output_path="summary.md"
)

# 🎯 NEW: Custom analysis with your own requirements
report = agent.run(
    input_path=["paper1.pdf", "paper2.pdf"],
    report_type="comparison",
    custom_prompt="compare the architectural innovations and their impact on performance",
    output_path="custom_analysis.md"
)

# Or step by step
papers = agent.load_papers("./papers/")
agent.analyze()
# Use custom analysis
agent.aggregate(custom_prompt="analyze the evolution of training techniques")
report = agent.generate_report("comparison")
```

## Configuration

### Environment Variables

The configuration file supports environment variable substitution with optional defaults:

```yaml
# Format: ${VAR_NAME:default_value}
provider: "${LLM_PROVIDER:openai}"      # Uses LLM_PROVIDER or "openai"
api_key: "${LLM_API_KEY:}"              # Uses LLM_API_KEY or empty string
api_base: "${LLM_API_BASE:}"            # Uses LLM_API_BASE or empty string
```

**Recommended setup** - Set environment variables for security:

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Or use generic LLM environment variables
export LLM_PROVIDER="deepseek"
export LLM_MODEL="deepseek-chat"
export LLM_API_KEY="your-api-key"
export LLM_API_BASE="https://api.deepseek.com"  # Optional, uses provider default
```

### LLM Providers

Supports multiple LLM providers with pre-configured endpoints:

| Provider | Example Models | Default API Base | API Key Env Var |
|----------|----------------|------------------|-----------------|
| openai | gpt-4o, gpt-4o-mini, gpt-4-turbo | https://api.openai.com/v1 | OPENAI_API_KEY |
| anthropic | claude-sonnet-4, claude-opus-4 | https://api.anthropic.com | ANTHROPIC_API_KEY |
| deepseek | deepseek-chat, deepseek-reasoner | https://api.deepseek.com | DEEPSEEK_API_KEY |
| zhipu | glm-4-plus, glm-4, glm-4-flash | https://open.bigmodel.cn/api/paas/v4 | ZHIPU_API_KEY |
| ollama | llama3.1, qwen2.5, deepseek-r1 | http://localhost:11434/v1 | (none required) |
| azure | gpt-4o, gpt-4 | (set AZURE_OPENAI_ENDPOINT) | AZURE_OPENAI_API_KEY |
| custom | (your models) | (set CUSTOM_LLM_ENDPOINT) | CUSTOM_LLM_API_KEY |

### Configuration File Structure

```yaml
# LLM settings - all support environment variable substitution
llm:
  provider: "${LLM_PROVIDER:openai}"    # Provider name
  model: "${LLM_MODEL:gpt-4o}"          # Model name
  api_key: "${LLM_API_KEY:}"            # API key (or use provider-specific env var)
  api_base: "${LLM_API_BASE:}"          # Custom endpoint (empty = use provider default)
  temperature: 0.3
  max_tokens: 4096
  timeout: 120
  max_retries: 3
  retry_delay: 2

# Provider presets - defines default endpoints and env var names
llm_providers:
  openai:
    api_base: "https://api.openai.com/v1"
    api_key_env: "OPENAI_API_KEY"       # Fallback env var for API key
    models: ["gpt-4o", "gpt-4o-mini"]
  # ... more providers

pdf_parser:
  engine: "pymupdf"                     # pymupdf or pdfplumber
  extract_tables: true

content_extractor:
  dimensions:
    - background
    - technology
    - experiment
    - result

knowledge_aggregator:
  comparison_dimensions:
    - architecture
    - training_method
    - performance

report_generator:
  output_format: "markdown"           # markdown, json, html
  language: "english"                  # english or chinese only (no auto)
  summary_level: "detailed"            # brief, detailed, comprehensive

parallel:
  enabled: true
  max_workers: 4
```

### Configuration Priority

The API key and endpoint are resolved in this order:

1. **Explicit value** in `llm` section (after environment variable substitution)
2. **Provider preset** - uses `api_key_env` to read from environment variable
3. **Default** - empty string (will cause error if required)

## Report Types

### Single Paper Summary (`single`)

Generates detailed reading notes for a single paper, including:
- Paper summary
- Research background
- Technical methods
- Experiment analysis
- Results and conclusions

### Multi-Paper Comparison (`comparison`)

#### Default Mode (without custom prompt)
Horizontally compares multiple papers with structured analysis:
- Overall summary
- Comparison matrix (by dimensions: architecture, training method, performance, etc.)
- Timeline of technology development
- Common themes and key differences
- Individual paper summaries

#### 🎯 Custom Analysis Mode (with `-p/--prompt`)
Provides focused analysis based on your specific requirements:
- **Flexible focus**: Analyze any aspect you care about (e.g., "compare data preprocessing approaches")
- **Targeted insights**: Get deep analysis on specific dimensions instead of general comparison
- **Natural language**: Simply describe what you want to analyze in plain language
- **Efficient output**: More concise and relevant to your needs

**Examples of custom prompts:**
- "analyze the differences in technical approaches"
- "compare data processing methods and their trade-offs"
- "evaluate architectural innovations and practical applications"
- "identify key improvements in training efficiency"
- "compare experimental setups and their validity"

### Technology Trend Analysis (`trend`)

Analyzes technology evolution across multiple papers, including:
- Technology timeline
- Identified trends
- Common themes
- Future directions

## Limitations and Constraints

Before using paper_agent, please be aware of the following limitations and constraints:

### 📄 PDF Processing Limitations

**Supported Formats**
- ✅ Text-based PDF files with extractable text
- ❌ Scanned PDFs (no OCR support)
- ❌ Image-only PDFs
- ❌ Password-protected PDFs
- ❌ Non-PDF formats (Word, LaTeX, HTML, etc.)

**Text Extraction Constraints**
- **Title extraction**: Improved pattern matching; handles most standard layouts reliably
- **Author extraction**: Limited to PDF metadata; text-based extraction not implemented
- **Abstract extraction**: Relies on "Abstract" section header; may miss abstracts without clear markers
- **Section detection**: Pattern-based; may miss non-standard section naming conventions
- **Table extraction**: ✅ **IMPROVED** - Automatically captures tables as images when text extraction fails; ensures complete visual fidelity
- **Figure captions**: Basic placeholder only; not truly extracted from PDF content
- **References**: Only parses numbered format `[1]` or `1.`; other citation styles may fail

**Layout Limitations**
- Multi-column layouts may result in scrambled text order
- Equations and mathematical symbols may not render correctly
- Footnotes and marginal notes may be misplaced
- Headers/footers may be included in main text

### 🤖 LLM-Related Limitations

**API Dependencies**
- **Internet required**: All LLM providers require network connectivity
- **API key required**: Must have valid API credentials (except Ollama)
- **Cost implications**: OpenAI, Anthropic, DeepSeek, etc. charge per token usage
- **Rate limits**: Subject to provider's API rate limits (not handled by tool)
- **Service availability**: Dependent on provider uptime

**Quality and Accuracy**
- **Hallucinations**: LLMs may generate plausible but incorrect information
- **Inconsistency**: Same paper may produce different analysis results across runs
- **Bias**: Analysis may reflect biases present in LLM training data
- **JSON parsing**: LLM must return valid JSON; failures can cause extraction errors
- **Language understanding**: Quality varies by language; best for English papers
- **Domain knowledge**: May struggle with highly specialized or novel concepts

**Performance Constraints**
- **Retry limit**: Default 3 retries on failure, then gives up
- **Timeout**: Default 120 seconds per request
- **No caching**: Same prompts are re-sent on every run (no result caching implemented)
- **Token limits**: Truncates content to fit within model's max_tokens (default 4096)

### 📊 Analysis Limitations

**Structural Constraints**
- **Fixed dimensions**: Analysis framework is hardcoded (background, technology, experiment, result)
- **Section patterns**: Only recognizes English section headers (Introduction, Method, Results, etc.)
- **Length limits**: Each dimension truncated to 2000 characters by default
- **No multilingual support**: Prompts and patterns optimized for English only

**Comparison Limitations**
- **Fixed comparison dimensions**: Architecture, training_method, performance (configurable but limited)
- **Timeline inference**: Relies on LLM to infer chronological order; may be inaccurate without publication dates
- **Trend analysis**: Quality entirely dependent on LLM capabilities
- **Custom prompts**: Results quality varies based on prompt clarity and LLM understanding

**Content Loss Risks**
- Important details may be lost due to text truncation
- Secondary contributions may be overlooked in favor of primary findings
- Nuanced arguments may be oversimplified
- Context-dependent information may be misinterpreted

### ⚡ Performance Limitations

**Processing Speed**
- **LLM bottleneck**: Analysis speed limited by LLM API response time (typically 10-60 seconds per paper)
- **No progress indication**: Long operations appear frozen (no live progress updates)
- **Serial LLM calls**: Multiple dimensions analyzed sequentially within each paper (parallelized across papers only)
- **Memory usage**: Entire PDF content loaded into memory; large PDFs or many PDFs consume significant RAM

**Scalability Constraints**
- **Parallel workers**: Default 4 workers; more doesn't help due to LLM API rate limits
- **No incremental processing**: Must re-analyze all papers on every run
- **No persistence**: No database or cache; results only saved as markdown files
- **Batch limits**: Analyzing 10+ papers simultaneously may hit API rate limits

### 🔧 Configuration Limitations

**Setup Requirements**
- **YAML only**: Configuration must be in YAML format
- **Manual API key setup**: No interactive configuration wizard
- **Limited validation**: Invalid config values may cause runtime errors
- **Provider-specific quirks**: Different LLM providers may behave differently

**Flexibility Constraints**
- **Fixed workflow**: Cannot customize the analysis pipeline order
- **No plugin system**: Cannot add custom analysis dimensions without code changes
- **Template limitations**: Report templates are hardcoded
- **Output formats**: Only markdown, JSON, HTML; no DOCX, PDF, etc.

### 🎯 Usage Scenarios

**✅ Well-Suited For:**
- Analyzing 1-10 academic papers in standard formats
- Comparing papers with similar structure and topics
- Getting quick high-level summaries of research papers
- Exploring new research areas with guided analysis
- English-language papers in computer science, AI/ML domains

**❌ Not Recommended For:**
- Production systems requiring high reliability
- Legal or medical documents requiring 100% accuracy
- Scanned documents or image-based PDFs
- Non-English papers (limited support)
- Papers in humanities, social sciences (analysis prompts optimized for technical papers)
- Large-scale batch processing (100+ papers)
- Real-time or interactive analysis systems
- Compliance-critical applications (no audit trail)

### 💡 Mitigations and Best Practices

**To Improve Results:**
- Use high-quality, text-extractable PDFs
- Verify LLM analysis against original paper content
- Run analysis multiple times for critical papers (cross-check consistency)
- Use higher-quality LLM models (e.g., GPT-4o, Claude Opus) for better accuracy
- Provide specific custom prompts for targeted analysis
- Review and edit generated reports before use

**Cost Management:**
- Use cheaper models (e.g., gpt-4o-mini, DeepSeek) for initial exploration
- Limit max_tokens to reduce per-request cost
- Use Ollama with local models for cost-free analysis (trade-off: lower quality)
- Batch related papers together to maximize context efficiency

## Project Structure

```
paper_agent/
├── core/                       # Core modules (~3900 lines)
│   ├── config.py               # Configuration management (342 lines)
│   ├── models.py               # Data models (187 lines)
│   ├── pdf_parser.py           # PDF parser with smart table screenshot (523 lines)
│   ├── structure_analyzer.py   # Structure analyzer (236 lines)
│   ├── llm_client.py           # LLM client (285 lines)
│   ├── content_extractor.py    # Content extractor with resource identification (493 lines)
│   ├── knowledge_aggregator.py # Knowledge aggregator (391 lines)
│   ├── report_generator.py     # Report generator with resource embedding (614 lines)
│   └── resource_manager.py     # Resource manager for figures/tables/equations (259 lines)
├── agent.py                    # Main agent class (234 lines)
├── main.py                     # CLI entry point (274 lines)
├── config.yaml                 # Default configuration
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## Dependencies

- Python >= 3.9
- PyMuPDF >= 1.23.0
- pdfplumber >= 0.10.0
- PyYAML >= 6.0
- openai >= 1.0.0
- anthropic >= 0.18.0
- markdown >= 3.5.0

## License

MIT License
