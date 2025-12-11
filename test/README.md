# Paper Agent Test Suite

Complete test suite for paper_agent, including unit tests and integration tests.

## Directory Structure

```
paper_agent/test/
├── unit/                   # Unit tests
│   └── test_agent.py      # Agent functionality tests
├── integration/           # Integration tests
│   └── test_scenarios.sh  # End-to-end scenario tests
├── test_data/             # Test data (if needed)
├── test_output/           # Test output files
└── README.md             # This file
```

## Test Cases Overview

### Unit Tests (test/unit/test_agent.py)

1. **test_agent_initialization** - Verify agent components are properly initialized
2. **test_load_single_paper** - Test loading a single PDF file
3. **test_load_multiple_papers** - Test loading multiple PDFs from directory
4. **test_analyze_papers** - Test paper analysis functionality
5. **test_custom_prompt_aggregation** - Test custom prompt feature structure
6. **test_resolve_paths** - Test path resolution (file, directory, glob)
7. **test_clear_cache** - Test cache clearing functionality

### Integration Tests (test/integration/test_scenarios.sh)

| Test # | Name | Description | Custom Prompt |
|--------|------|-------------|---------------|
| 1 | Single Paper Analysis | Analyze one paper using default mode | No |
| 2 | Comparison (Default) | Compare two papers using default analysis | No |
| 3 | Technical Approach | Compare technical approaches | "分析技术路线的差异" |
| 4 | Data Processing | Compare data processing methods | "对比两篇论文在数据处理方法上的优缺点" |
| 5 | Innovation Analysis | Analyze innovation and application value | "分析模型架构的创新点和实际应用价值" |
| 6 | JSON Output | Test JSON output format | No |
| 7 | Multiple Comparison | Compare 3+ papers | No |
| 8 | Trend Analysis | Analyze technology trends across papers | No |
| 9 | Custom Title | Test custom report title | No |
| 10 | Directory Input | Analyze all papers in a directory | No |

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-cov

# Ensure paper_agent is installed
cd /root/paper_summary
pip install -e paper_agent/ --break-system-packages

# Set up configuration
# Edit config.yaml with your API key
```

### Run Unit Tests

```bash
# Run all unit tests
cd /root/paper_summary
pytest paper_agent/test/unit/ -v

# Run specific test file
pytest paper_agent/test/unit/test_agent.py -v

# Run with coverage report
pytest paper_agent/test/unit/ --cov=paper_agent --cov-report=html
```

### Run Integration Tests

```bash
# Run all integration tests
cd /root/paper_summary
./paper_agent/test/integration/test_scenarios.sh

# The script will:
# 1. Find all PDFs in origin/paper/
# 2. Run 10 different test scenarios
# 3. Generate reports in paper_agent/test/test_output/
# 4. Show pass/fail summary
```

## Test Output

All test outputs are saved to `paper_agent/test/test_output/`:
- `test1_single_default.md` - Single paper analysis
- `test2_comparison_default.md` - Default comparison
- `test3_custom_technical.md` - Custom technical analysis
- `test4_custom_data.md` - Custom data processing analysis
- `test5_custom_innovation.md` - Custom innovation analysis
- `test6_json.json` - JSON format output
- `test7_multiple.md` - Multiple papers comparison
- `test8_trend.md` - Trend analysis
- `test9_custom_title.md` - Custom title report
- `test10_directory.md` - Directory analysis
- `test*.log` - Execution logs for each test

## Custom Prompt Test Examples

The integration tests include several custom prompt examples:

### Example 1: Technical Approach Comparison
```bash
python3 -m paper_agent.main analyze paper1.pdf paper2.pdf \
  -t comparison -p "分析技术路线的差异"
```

**Expected Output:**
- Comparison of research approaches
- Method differences
- Architecture comparisons
- Training strategies

### Example 2: Data Processing Analysis
```bash
python3 -m paper_agent.main analyze paper1.pdf paper2.pdf \
  -t comparison -p "对比两篇论文在数据处理方法上的优缺点"
```

**Expected Output:**
- Data processing methodologies
- Pros and cons of each approach
- Efficiency comparisons

### Example 3: Innovation Analysis
```bash
python3 -m paper_agent.main analyze paper1.pdf paper2.pdf \
  -t comparison -p "分析模型架构的创新点和实际应用价值"
```

**Expected Output:**
- Architectural innovations
- Practical application value
- Real-world use cases

## Adding New Test Cases

### Adding Unit Tests

1. Open `paper_agent/test/unit/test_agent.py`
2. Add new test method to `TestPaperAgent` class:

```python
def test_new_feature(self, agent):
    """Test new feature"""
    # Your test code here
    assert condition
```

### Adding Integration Tests

1. Open `paper_agent/test/integration/test_scenarios.sh`
2. Add new test block following the template:

```bash
# ==========================================
# Test N: Your Test Name
# ==========================================
print_test_header "Your Test Description"

python3 -m paper_agent.main analyze ... \
    2>&1 | tee "$OUTPUT_DIR/testN.log"

if [ -f "$OUTPUT_DIR/testN_output.md" ]; then
    print_result 0 "Your test name"
else
    print_result 1 "Your test name"
fi
```

## Troubleshooting

### Issue: API Key Not Set
```
Error: API key not configured
```
**Solution:** Set API key in config.yaml

### Issue: PDF Files Not Found
```
Error: No PDF files found in origin/paper/
```
**Solution:** Ensure PDFs exist in `origin/paper/` directory

### Issue: Tests Timeout
```
Error: Request timeout after 120s
```
**Solution:** Increase timeout in config.yaml:
```yaml
llm:
  timeout: 300
```

## Test Metrics

The integration test suite provides:
- ✓ Passed tests count
- ✗ Failed tests count
- ⊘ Skipped tests count
- Individual test logs for debugging

## Quick Start

Run all tests:
```bash
cd /root/paper_summary
./paper_agent/test/integration/test_scenarios.sh
```

## License

Same as paper_agent (MIT License)
