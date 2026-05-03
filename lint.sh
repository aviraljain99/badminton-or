#!/bin/bash

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

usage() {
    cat << EOF
Usage: $0 [target]

Targets:
  format    - Run code formatter (ruff format)
  lint      - Run linter (ruff check)
  check     - Run both linter and formatter in check mode (no changes)
  all       - Run formatter and linter
  help      - Show this help message

If no target is provided, defaults to 'all'.
EOF
}

format() {
    echo -e "${BLUE}Running formatter...${NC}"
    uv run ruff format . --line-length 100
    echo -e "${GREEN}✓ Formatting complete${NC}"
}

lint() {
    echo -e "${BLUE}Running linter...${NC}"
    uv run ruff check .
    echo -e "${GREEN}✓ Linting complete${NC}"
}

check() {
    echo -e "${BLUE}Running checks (no changes)...${NC}"
    uv run ruff check . --no-fix
    uv run ruff format . --check
    echo -e "${GREEN}✓ Checks passed${NC}"
}

all() {
    lint
    format
}

# Parse arguments
TARGET="${1:-all}"

case "$TARGET" in
    format)
        format
        ;;
    lint)
        lint
        ;;
    check)
        check
        ;;
    all)
        all
        ;;
    help)
        usage
        ;;
    *)
        echo "Unknown target: $TARGET"
        echo ""
        usage
        exit 1
        ;;
esac
