"""
Paper Agent CLI Entry Point
"""
import argparse
import sys
import os

from .agent import PaperAgent


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        prog="paper-agent",
        description="Paper Reading Agent - Intelligent paper analysis tool powered by LLM",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze papers and generate reports"
    )
    analyze_parser.add_argument(
        "input",
        nargs="+",
        help="Input PDF file paths (can specify multiple)"
    )
    analyze_parser.add_argument(
        "-t", "--type",
        choices=["single", "comparison", "trend"],
        default="single",
        help="Report type: single (single paper summary), comparison (multi-paper comparison), trend (technology trend analysis)"
    )
    analyze_parser.add_argument(
        "-o", "--output",
        help="Output file path"
    )
    analyze_parser.add_argument(
        "--title",
        help="Report title"
    )
    analyze_parser.add_argument(
        "-c", "--config",
        help="Configuration file path"
    )
    analyze_parser.add_argument(
        "-f", "--format",
        choices=["markdown", "json", "html"],
        default="markdown",
        help="Output format"
    )
    analyze_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show verbose output"
    )
    analyze_parser.add_argument(
        "-p", "--prompt",
        help="Custom analysis requirement (e.g., 'analyze differences in technical approaches')"
    )

    # init command
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize configuration file"
    )
    init_parser.add_argument(
        "-o", "--output",
        default="config.yaml",
        help="Output configuration file path"
    )

    args = parser.parse_args()

    if args.command == "analyze":
        run_analyze(args)
    elif args.command == "init":
        run_init(args)
    else:
        parser.print_help()


def run_analyze(args):
    """Execute analysis command"""
    try:
        # Create agent
        agent = PaperAgent(config_path=args.config)

        # Set output format
        if args.format:
            agent.config.report_generator.output_format = args.format

        # Get input files
        input_paths = args.input

        # Determine output path
        output_path = args.output
        if not output_path:
            # Generate default output filename
            if len(input_paths) == 1 and os.path.isfile(input_paths[0]):
                base_name = os.path.splitext(os.path.basename(input_paths[0]))[0]
                output_path = f"{base_name}_summary.md"
            else:
                output_path = f"papers_{args.type}_report.md"

        # Execute analysis
        report = agent.run(
            input_path=input_paths,
            report_type=args.type,
            output_path=output_path,
            title=args.title,
            custom_prompt=args.prompt,  # Pass custom prompt
        )

        print(f"\nAnalysis complete!")
        print(f"Report saved to: {output_path}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def run_init(args):
    """Execute initialization command"""
    config_template = '''# Paper Reading Agent Configuration

# =============================================================================
# LLM Configuration
# =============================================================================
# All values support environment variable substitution: ${VAR_NAME:default}

llm:
  # Provider name: openai, anthropic, deepseek, zhipu, ollama, azure, custom
  provider: "${LLM_PROVIDER:openai}"

  # Model name (varies by provider)
  # Examples: gpt-4o, claude-sonnet-4-20250514, deepseek-chat, glm-4-plus
  model: "${LLM_MODEL:gpt-4o}"

  # API Key - Set via environment variable for security
  api_key: "${LLM_API_KEY:}"

  # API Base URL (Endpoint) - Leave empty to use provider default
  api_base: "${LLM_API_BASE:}"

  # Model parameters
  temperature: 0.3          # 0.0 (deterministic) to 1.0 (creative)
  max_tokens: 4096          # Maximum response length
  timeout: 120              # Request timeout in seconds

  # Retry configuration
  max_retries: 3
  retry_delay: 2

# =============================================================================
# Provider Presets (API endpoints and env var names)
# =============================================================================
llm_providers:
  openai:
    api_base: "https://api.openai.com/v1"
    api_key_env: "OPENAI_API_KEY"
    models: ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]

  anthropic:
    api_base: "https://api.anthropic.com"
    api_key_env: "ANTHROPIC_API_KEY"
    models: ["claude-sonnet-4-20250514", "claude-opus-4-20250514"]

  deepseek:
    api_base: "https://api.deepseek.com"
    api_key_env: "DEEPSEEK_API_KEY"
    models: ["deepseek-chat", "deepseek-reasoner"]

  zhipu:
    api_base: "https://open.bigmodel.cn/api/paas/v4"
    api_key_env: "ZHIPU_API_KEY"
    models: ["glm-4-plus", "glm-4", "glm-4-flash"]

  ollama:
    api_base: "http://localhost:11434/v1"
    api_key_env: ""
    models: ["llama3.1", "qwen2.5", "deepseek-r1"]

  azure:
    api_base: "${AZURE_OPENAI_ENDPOINT:}"
    api_key_env: "AZURE_OPENAI_API_KEY"
    models: ["gpt-4o", "gpt-4"]

  custom:
    api_base: "${CUSTOM_LLM_ENDPOINT:}"
    api_key_env: "CUSTOM_LLM_API_KEY"
    models: []

# =============================================================================
# PDF Parser Configuration
# =============================================================================
pdf_parser:
  engine: "pymupdf"         # pymupdf (recommended) or pdfplumber
  extract_images: true      # Extract images for key figures in report
  extract_tables: true
  max_pages: 0              # 0 = no limit

# =============================================================================
# Content Extractor Configuration
# =============================================================================
content_extractor:
  dimensions:
    - background            # Research background
    - technology            # Core technology
    - experiment            # Experiment analysis
    - result                # Result analysis
  max_length_per_dimension: 2000
  extract_keywords: true
  num_keywords: 10

# =============================================================================
# Knowledge Aggregator Configuration
# =============================================================================
knowledge_aggregator:
  comparison_dimensions:
    - architecture          # Model architecture
    - training_method       # Training method
    - data_scale            # Data scale
    - performance           # Performance metrics
    - efficiency            # Computational efficiency
  generate_timeline: true
  analyze_trends: true

# Report Generator Configuration
# =============================================================================
report_generator:
  output_format: "markdown"    # markdown, json, html
  language: "english"           # english or chinese (NO auto option)
  include_quotes: true
  summary_level: "detailed"     # brief, detailed, comprehensive

# =============================================================================
# Parallel Processing Configuration
# =============================================================================
parallel:
  enabled: true
  max_workers: 4

# =============================================================================
# Logging Configuration
# =============================================================================
logging:
  level: "INFO"             # DEBUG, INFO, WARNING, ERROR
'''

    output_path = args.output

    if os.path.exists(output_path):
        confirm = input(f"{output_path} already exists, overwrite? (y/N): ")
        if confirm.lower() != 'y':
            print("Cancelled")
            return

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(config_template)

    print(f"Configuration file created: {output_path}")
    print("\nNext steps:")
    print("1. Edit the configuration file, set your LLM API key")
    print("2. Run: paper-agent analyze your_paper.pdf")


if __name__ == "__main__":
    main()
