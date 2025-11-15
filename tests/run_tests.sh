#!/bin/bash

# =============================================================================
# SecurityEvaluator - One-Command Test Script
# =============================================================================
# This script automates the testing process by:
# 1. Starting the Purple Agent (target system)
# 2. Waiting for it to be ready
# 3. Running the comprehensive test suite
# 4. Cleaning up processes when done
#
# Usage:
#   ./tests/run_tests.sh
#
# Requirements:
#   - Python 3.7+
#   - Dependencies installed (pip install -r requirements.txt)
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PURPLE_AGENT_PORT=8000
PURPLE_AGENT_URL="http://127.0.0.1:${PURPLE_AGENT_PORT}"
PURPLE_AGENT_SCRIPT="purple_agents/home_automation_agent.py"
TEST_SCRIPT="tests/test_final_comprehensive.py"
MAX_WAIT_TIME=10  # seconds to wait for Purple Agent to start
VENV_PATH=".venv"

# Track Purple Agent PID for cleanup
PURPLE_AGENT_PID=""

# =============================================================================
# CLEANUP FUNCTION
# =============================================================================
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up...${NC}"

    # Kill Purple Agent if it's running
    if [ -n "$PURPLE_AGENT_PID" ]; then
        echo -e "${BLUE}Stopping Purple Agent (PID: $PURPLE_AGENT_PID)${NC}"
        kill $PURPLE_AGENT_PID 2>/dev/null || true
    fi

    # Kill any remaining processes on the port
    lsof -ti:${PURPLE_AGENT_PORT} 2>/dev/null | xargs kill -9 2>/dev/null || true

    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

# Register cleanup to run on script exit
trap cleanup EXIT INT TERM

# =============================================================================
# CHECK PREREQUISITES
# =============================================================================
echo -e "${BLUE}🔍 Checking prerequisites...${NC}"

# Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: python3 is not installed${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ -d "$VENV_PATH" ]; then
    echo -e "${GREEN}✅ Found virtual environment at $VENV_PATH${NC}"
    # Activate virtual environment
    source "$VENV_PATH/bin/activate"
    echo -e "${GREEN}✅ Virtual environment activated${NC}"
    PYTHON_CMD="python"
else
    echo -e "${YELLOW}⚠️  No virtual environment found at $VENV_PATH${NC}"
    echo -e "${YELLOW}⚠️  Using system Python3${NC}"
    PYTHON_CMD="python3"
fi

# Check if Purple Agent script exists
if [ ! -f "$PURPLE_AGENT_SCRIPT" ]; then
    echo -e "${RED}❌ Error: Purple Agent script not found at $PURPLE_AGENT_SCRIPT${NC}"
    exit 1
fi

# Check if test script exists
if [ ! -f "$TEST_SCRIPT" ]; then
    echo -e "${RED}❌ Error: Test script not found at $TEST_SCRIPT${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}\n"

# =============================================================================
# START PURPLE AGENT
# =============================================================================
echo -e "${BLUE}🚀 Starting Purple Agent on port ${PURPLE_AGENT_PORT}...${NC}"

# Kill any existing processes on the port
lsof -ti:${PURPLE_AGENT_PORT} 2>/dev/null | xargs kill -9 2>/dev/null || true
sleep 1

# Start Purple Agent in background
$PYTHON_CMD "$PURPLE_AGENT_SCRIPT" --port ${PURPLE_AGENT_PORT} > /tmp/purple_agent.log 2>&1 &
PURPLE_AGENT_PID=$!

echo -e "${BLUE}Purple Agent started with PID: ${PURPLE_AGENT_PID}${NC}"

# =============================================================================
# WAIT FOR PURPLE AGENT TO BE READY
# =============================================================================
echo -e "${YELLOW}⏳ Waiting for Purple Agent to be ready...${NC}"

WAIT_COUNT=0
while [ $WAIT_COUNT -lt $MAX_WAIT_TIME ]; do
    if curl -s "${PURPLE_AGENT_URL}/.well-known/agent-card.json" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Purple Agent is ready!${NC}\n"
        break
    fi

    # Check if Purple Agent process is still running
    if ! kill -0 $PURPLE_AGENT_PID 2>/dev/null; then
        echo -e "${RED}❌ Error: Purple Agent process died${NC}"
        echo -e "${YELLOW}Last 20 lines of log:${NC}"
        tail -20 /tmp/purple_agent.log
        exit 1
    fi

    sleep 1
    WAIT_COUNT=$((WAIT_COUNT + 1))
    echo -n "."
done

if [ $WAIT_COUNT -eq $MAX_WAIT_TIME ]; then
    echo -e "\n${RED}❌ Error: Purple Agent failed to start within ${MAX_WAIT_TIME} seconds${NC}"
    echo -e "${YELLOW}Last 20 lines of log:${NC}"
    tail -20 /tmp/purple_agent.log
    exit 1
fi

# =============================================================================
# RUN TESTS
# =============================================================================
echo -e "${BLUE}🧪 Running comprehensive test suite...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Run the test script
if python3 "$TEST_SCRIPT"; then
    TEST_EXIT_CODE=0
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ Tests completed successfully!${NC}\n"
else
    TEST_EXIT_CODE=$?
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ Tests failed with exit code ${TEST_EXIT_CODE}${NC}\n"
fi

# =============================================================================
# DISPLAY RESULTS
# =============================================================================
echo -e "${BLUE}📊 Test Results Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check if reports were generated
REPORT_DIR="reports"
if [ -d "$REPORT_DIR" ]; then
    LATEST_REPORTS=$(ls -t "$REPORT_DIR" 2>/dev/null | head -5)
    if [ -n "$LATEST_REPORTS" ]; then
        echo -e "${GREEN}📁 Reports generated in: ${REPORT_DIR}/${NC}"
        echo "$LATEST_REPORTS" | while read -r report; do
            echo -e "   - ${report}"
        done
    fi
else
    echo -e "${YELLOW}⚠️  No reports directory found${NC}"
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# =============================================================================
# EXIT
# =============================================================================
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    echo -e "${BLUE}💡 Next steps:${NC}"
    echo -e "   - Review reports in the '${REPORT_DIR}' directory"
    echo -e "   - Check security scores and recommendations"
    echo -e "   - Iterate on Purple Agent security improvements\n"
else
    echo -e "${RED}⚠️  Some tests failed. Please review the output above.${NC}\n"
fi

exit $TEST_EXIT_CODE
