#!/bin/bash
# Quick test runner for Paper Agent
# Run this from the project root: ./paper_agent/test/run_tests.sh

set -e

echo "=========================================="
echo "Paper Agent Test Runner"
echo "=========================================="
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../.."

echo "Working directory: $(pwd)"
echo ""

# Parse arguments
TEST_TYPE="${1:-all}"

case "$TEST_TYPE" in
    unit)
        echo "Running unit tests only..."
        pytest paper_agent/test/unit/ -v
        ;;
    integration)
        echo "Running integration tests only..."
        ./paper_agent/test/integration/test_scenarios.sh
        ;;
    all)
        echo "Running all tests..."
        echo ""
        echo "=== Unit Tests ==="
        pytest paper_agent/test/unit/ -v || true
        echo ""
        echo "=== Integration Tests ==="
        ./paper_agent/test/integration/test_scenarios.sh
        ;;
    *)
        echo "Usage: $0 [unit|integration|all]"
        echo ""
        echo "  unit         - Run unit tests only"
        echo "  integration  - Run integration tests only"
        echo "  all          - Run all tests (default)"
        exit 1
        ;;
esac

echo ""
echo "Tests completed!"
