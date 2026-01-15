#!/bin/bash
# Claude Code Proxy - Easy runner script
# Usage: ./run.sh [command]

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║           Claude Code Proxy - Request Capture             ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_help() {
    print_header
    echo "Usage: ./run.sh [command]"
    echo ""
    echo "Commands:"
    echo "  proxy      Start the mitmproxy server (run this first)"
    echo "  setup      Print environment setup commands for Claude"
    echo "  export     Export captured data to readable text file"
    echo "  summary    Show summary of captured data"
    echo "  view       Open the latest capture in your text editor"
    echo "  clean      Remove all captured data"
    echo "  help       Show this help message"
    echo ""
    echo "Quick Start:"
    echo "  1. Terminal 1: ./run.sh proxy"
    echo "  2. Terminal 2: source env.sh && claude \"hello\""
    echo "  3. Terminal 2: ./run.sh export"
    echo ""
}

check_mitmproxy() {
    if ! command -v mitmdump &> /dev/null; then
        echo -e "${RED}Error: mitmproxy is not installed${NC}"
        echo "Install it with: pip install mitmproxy"
        exit 1
    fi
}

case "${1:-help}" in
    proxy|start)
        print_header
        check_mitmproxy
        echo -e "${GREEN}Starting proxy on port 8080...${NC}"
        echo ""
        echo -e "${YELLOW}In another terminal, run:${NC}"
        echo "  cd $PROJECT_DIR"
        echo "  source env.sh"
        echo "  claude \"your prompt\""
        echo ""
        echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
        echo ""
        mitmdump -s src/capture.py --listen-port 8080
        ;;

    setup|env)
        echo "Run this in your terminal before using Claude:"
        echo ""
        echo "export HTTPS_PROXY=http://127.0.0.1:8080"
        echo "export HTTP_PROXY=http://127.0.0.1:8080"
        echo "export NODE_EXTRA_CA_CERTS=~/.mitmproxy/mitmproxy-ca-cert.pem"
        echo ""
        echo "Or simply: source env.sh"
        ;;

    export)
        python3 src/export.py
        ;;

    summary)
        python3 src/export.py --summary
        ;;

    view|open)
        if [ -f "output/claude_code_captured.json" ]; then
            # Export first
            python3 src/export.py
            # Find the most recent txt file
            LATEST=$(ls -t output/*.txt 2>/dev/null | head -1)
            if [ -n "$LATEST" ]; then
                echo "Opening $LATEST..."
                open "$LATEST" 2>/dev/null || xdg-open "$LATEST" 2>/dev/null || less "$LATEST"
            fi
        else
            echo -e "${RED}No capture found. Run Claude through the proxy first.${NC}"
        fi
        ;;

    clean)
        echo "Removing captured data..."
        rm -f output/*.json output/*.jsonl output/*.txt
        echo -e "${GREEN}Done.${NC}"
        ;;

    help|--help|-h)
        print_help
        ;;

    *)
        echo -e "${RED}Unknown command: $1${NC}"
        print_help
        exit 1
        ;;
esac
