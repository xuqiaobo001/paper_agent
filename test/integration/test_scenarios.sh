#!/bin/bash
# Paper Agent Integration Test Suite
# Tests various usage scenarios

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test configuration
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname $(dirname $(dirname $TEST_DIR)))"
OUTPUT_DIR="$TEST_DIR/../test_output"
PAPER_DIR="$ROOT_DIR/origin/paper"

# Counters
PASSED=0
FAILED=0
SKIPPED=0

# Helper functions
print_test_header() {
    echo ""
    echo "=========================================="
    echo "TEST: $1"
    echo "=========================================="
}

print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASSED${NC}: $2"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}: $2"
        ((FAILED++))
    fi
}

skip_test() {
    echo -e "${YELLOW}⊘ SKIPPED${NC}: $1"
    ((SKIPPED++))
}

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Check if papers exist
if [ ! -d "$PAPER_DIR" ]; then
    echo -e "${RED}Error: Paper directory not found: $PAPER_DIR${NC}"
    exit 1
fi

PAPERS=($(ls "$PAPER_DIR"/*.pdf 2>/dev/null))
if [ ${#PAPERS[@]} -eq 0 ]; then
    echo -e "${RED}Error: No PDF files found in $PAPER_DIR${NC}"
    exit 1
fi

echo "Found ${#PAPERS[@]} PDF files for testing"
echo "Test output directory: $OUTPUT_DIR"
echo ""

# ==========================================
# Test 1: Single Paper Analysis (Default)
# ==========================================
print_test_header "Single Paper Analysis - Default Mode"

python3 -m paper_agent.main analyze "${PAPERS[0]}" \
    -o "$OUTPUT_DIR/test1_single_default.md" \
    -t single \
    2>&1 | tee "$OUTPUT_DIR/test1.log"

if [ -f "$OUTPUT_DIR/test1_single_default.md" ] && [ -s "$OUTPUT_DIR/test1_single_default.md" ]; then
    print_result 0 "Single paper analysis (default mode)"
else
    print_result 1 "Single paper analysis (default mode)"
fi

# ==========================================
# Test 2: Comparison Analysis (Default)
# ==========================================
print_test_header "Two Papers Comparison - Default Mode"

if [ ${#PAPERS[@]} -ge 2 ]; then
    python3 -m paper_agent.main analyze "${PAPERS[0]}" "${PAPERS[1]}" \
        -o "$OUTPUT_DIR/test2_comparison_default.md" \
        -t comparison \
        2>&1 | tee "$OUTPUT_DIR/test2.log"

    if [ -f "$OUTPUT_DIR/test2_comparison_default.md" ] && [ -s "$OUTPUT_DIR/test2_comparison_default.md" ]; then
        print_result 0 "Two papers comparison (default mode)"
    else
        print_result 1 "Two papers comparison (default mode)"
    fi
else
    skip_test "Two papers comparison (not enough papers)"
fi

# ==========================================
# Test 3: Custom Prompt - Technical Approach
# ==========================================
print_test_header "Custom Prompt - Technical Approach Differences"

if [ ${#PAPERS[@]} -ge 2 ]; then
    python3 -m paper_agent.main analyze "${PAPERS[0]}" "${PAPERS[1]}" \
        -o "$OUTPUT_DIR/test3_custom_technical.md" \
        -t comparison \
        -p "分析技术路线的差异" \
        2>&1 | tee "$OUTPUT_DIR/test3.log"

    if [ -f "$OUTPUT_DIR/test3_custom_technical.md" ] && [ -s "$OUTPUT_DIR/test3_custom_technical.md" ]; then
        # Check if custom analysis is present
        if grep -q "技术路线" "$OUTPUT_DIR/test3_custom_technical.md"; then
            print_result 0 "Custom prompt - technical approach"
        else
            print_result 1 "Custom prompt - technical approach (content not found)"
        fi
    else
        print_result 1 "Custom prompt - technical approach"
    fi
else
    skip_test "Custom prompt test (not enough papers)"
fi

# ==========================================
# Test 4: Custom Prompt - Data Processing
# ==========================================
print_test_header "Custom Prompt - Data Processing Methods"

if [ ${#PAPERS[@]} -ge 2 ]; then
    python3 -m paper_agent.main analyze "${PAPERS[0]}" "${PAPERS[1]}" \
        -o "$OUTPUT_DIR/test4_custom_data.md" \
        -t comparison \
        -p "对比两篇论文在数据处理方法上的优缺点" \
        2>&1 | tee "$OUTPUT_DIR/test4.log"

    if [ -f "$OUTPUT_DIR/test4_custom_data.md" ] && [ -s "$OUTPUT_DIR/test4_custom_data.md" ]; then
        print_result 0 "Custom prompt - data processing"
    else
        print_result 1 "Custom prompt - data processing"
    fi
else
    skip_test "Custom prompt test (not enough papers)"
fi

# ==========================================
# Test 5: Custom Prompt - Innovation Analysis
# ==========================================
print_test_header "Custom Prompt - Innovation Analysis"

if [ ${#PAPERS[@]} -ge 2 ]; then
    python3 -m paper_agent.main analyze "${PAPERS[0]}" "${PAPERS[1]}" \
        -o "$OUTPUT_DIR/test5_custom_innovation.md" \
        -t comparison \
        -p "分析模型架构的创新点和实际应用价值" \
        2>&1 | tee "$OUTPUT_DIR/test5.log"

    if [ -f "$OUTPUT_DIR/test5_custom_innovation.md" ] && [ -s "$OUTPUT_DIR/test5_custom_innovation.md" ]; then
        print_result 0 "Custom prompt - innovation analysis"
    else
        print_result 1 "Custom prompt - innovation analysis"
    fi
else
    skip_test "Custom prompt test (not enough papers)"
fi

# ==========================================
# Test 6: JSON Output Format
# ==========================================
print_test_header "JSON Output Format"

python3 -m paper_agent.main analyze "${PAPERS[0]}" \
    -o "$OUTPUT_DIR/test6_json.json" \
    -t single \
    -f json \
    2>&1 | tee "$OUTPUT_DIR/test6.log"

if [ -f "$OUTPUT_DIR/test6_json.json" ] && [ -s "$OUTPUT_DIR/test6_json.json" ]; then
    # Validate JSON format
    if python3 -c "import json; json.load(open('$OUTPUT_DIR/test6_json.json'))" 2>/dev/null; then
        print_result 0 "JSON output format"
    else
        print_result 1 "JSON output format (invalid JSON)"
    fi
else
    print_result 1 "JSON output format"
fi

# ==========================================
# Test 7: Multiple Papers Comparison
# ==========================================
print_test_header "Multiple Papers Comparison (3+ papers)"

if [ ${#PAPERS[@]} -ge 3 ]; then
    python3 -m paper_agent.main analyze "${PAPERS[0]}" "${PAPERS[1]}" "${PAPERS[2]}" \
        -o "$OUTPUT_DIR/test7_multiple.md" \
        -t comparison \
        2>&1 | tee "$OUTPUT_DIR/test7.log"

    if [ -f "$OUTPUT_DIR/test7_multiple.md" ] && [ -s "$OUTPUT_DIR/test7_multiple.md" ]; then
        print_result 0 "Multiple papers comparison"
    else
        print_result 1 "Multiple papers comparison"
    fi
else
    skip_test "Multiple papers comparison (not enough papers)"
fi

# ==========================================
# Test 8: Trend Analysis
# ==========================================
print_test_header "Trend Analysis"

if [ ${#PAPERS[@]} -ge 3 ]; then
    python3 -m paper_agent.main analyze "${PAPERS[0]}" "${PAPERS[1]}" "${PAPERS[2]}" \
        -o "$OUTPUT_DIR/test8_trend.md" \
        -t trend \
        2>&1 | tee "$OUTPUT_DIR/test8.log"

    if [ -f "$OUTPUT_DIR/test8_trend.md" ] && [ -s "$OUTPUT_DIR/test8_trend.md" ]; then
        print_result 0 "Trend analysis"
    else
        print_result 1 "Trend analysis"
    fi
else
    skip_test "Trend analysis (not enough papers)"
fi

# ==========================================
# Test 9: Custom Title
# ==========================================
print_test_header "Custom Report Title"

python3 -m paper_agent.main analyze "${PAPERS[0]}" \
    -o "$OUTPUT_DIR/test9_custom_title.md" \
    -t single \
    --title "My Custom Report Title" \
    2>&1 | tee "$OUTPUT_DIR/test9.log"

if [ -f "$OUTPUT_DIR/test9_custom_title.md" ] && [ -s "$OUTPUT_DIR/test9_custom_title.md" ]; then
    if grep -q "My Custom Report Title" "$OUTPUT_DIR/test9_custom_title.md"; then
        print_result 0 "Custom report title"
    else
        print_result 1 "Custom report title (title not found)"
    fi
else
    print_result 1 "Custom report title"
fi

# ==========================================
# Test 10: Directory Input
# ==========================================
print_test_header "Directory Input Analysis"

if [ ${#PAPERS[@]} -ge 2 ]; then
    python3 -m paper_agent.main analyze "$PAPER_DIR" \
        -o "$OUTPUT_DIR/test10_directory.md" \
        -t trend \
        2>&1 | tee "$OUTPUT_DIR/test10.log"

    if [ -f "$OUTPUT_DIR/test10_directory.md" ] && [ -s "$OUTPUT_DIR/test10_directory.md" ]; then
        print_result 0 "Directory input analysis"
    else
        print_result 1 "Directory input analysis"
    fi
else
    skip_test "Directory input analysis (not enough papers)"
fi

# ==========================================
# Print Summary
# ==========================================
echo ""
echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo -e "${GREEN}Passed:${NC}  $PASSED"
echo -e "${RED}Failed:${NC}  $FAILED"
echo -e "${YELLOW}Skipped:${NC} $SKIPPED"
echo "Total:   $((PASSED + FAILED + SKIPPED))"
echo ""
echo "Test outputs saved to: $OUTPUT_DIR"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed! Check logs in $OUTPUT_DIR${NC}"
    exit 1
fi
