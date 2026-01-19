#!/bin/bash

# Test script for News Agent
# Demonstrates two ways to interact with the news-agent via Agent Gateway:
# 1. OpenAI-compatible API
# 2. A2A protocol

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_GATEWAY_URL="${AGENT_GATEWAY_URL:-http://localhost:8004}"

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed. Install with 'brew install jq' for formatted output."
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}News Agent Test${NC}"
echo -e "${BLUE}========================================${NC}"

# Function to test Agent Gateway (OpenAI-compatible API)
test_openai_api() {
    echo -e "${GREEN}[1] Testing via Agent Gateway - OpenAI-compatible API${NC}"
    echo -e "    Endpoint: ${AGENT_GATEWAY_URL}/chat/completions"
    echo ""

    curl -vfs "${AGENT_GATEWAY_URL}/chat/completions" \
        -H "Content-Type: application/json" \
        -d '{
            "model": "showcase-news/news-agent",
            "messages": [
                {
                    "role": "user",
                    "content": "What are the latest headlines in technology news?"
                }
            ]
        }' | jq

    echo ""
    echo -e "${GREEN}✓ OpenAI-compatible API test complete${NC}"
    echo ""
}

# Function to test Agent Gateway (A2A protocol)
test_a2a_protocol() {
    echo -e "${GREEN}[2] Testing via Agent Gateway - A2A Protocol${NC}"
    echo -e "    Endpoint: ${AGENT_GATEWAY_URL}/news-agent/"
    echo ""

    # Generate a random message ID and context ID
    MESSAGE_ID=$(uuidgen 2>/dev/null || echo "$(date +%s)-$RANDOM")
    CONTEXT_ID=$(uuidgen 2>/dev/null || echo "$(date +%s)-$RANDOM")

    curl -vfs "${AGENT_GATEWAY_URL}/news-agent" \
        -H "Content-Type: application/json" \
        -d "$(jq -n --arg msg_id "$MESSAGE_ID" --arg ctx_id "$CONTEXT_ID" '{
           "jsonrpc": "2.0",
           "id": 1,
           "method": "message/send",
           "params": {
               "message": {
                   "role": "user",
                   "parts": [
                       {
                           "kind": "text",
                           "text": "What are the latest headlines in technology news?"
                       }
                   ],
                   "messageId": $msg_id,
                   "contextId": $ctx_id
               },
               "metadata": {}
           }
       }')" | jq

    echo ""
    echo -e "${GREEN}✓ A2A protocol test complete${NC}"
    echo ""
}

# Parse command line arguments
METHOD="${1:-all}"

case "$METHOD" in
    openai)
        test_openai_api
        ;;
    a2a)
        test_a2a_protocol
        ;;
    all)
        test_openai_api
        echo ""
        echo -e "${BLUE}----------------------------------------${NC}"
        echo ""
        test_a2a_protocol
        ;;
    *)
        echo "Usage: $0 [openai|a2a|all]"
        echo ""
        echo "  openai  - Test via Agent Gateway (OpenAI-compatible API)"
        echo "  a2a     - Test via Agent Gateway (A2A protocol)"
        echo "  all     - Test both protocols (default)"
        echo ""
        echo "Environment variables:"
        echo "  AGENT_GATEWAY_URL - Agent Gateway URL"
        exit 1
        ;;
esac
