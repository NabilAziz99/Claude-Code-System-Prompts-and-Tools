#!/bin/bash
# Source this file to configure proxy environment
# Usage: source env.sh

export HTTPS_PROXY=http://127.0.0.1:8080
export HTTP_PROXY=http://127.0.0.1:8080
export NODE_EXTRA_CA_CERTS=~/.mitmproxy/mitmproxy-ca-cert.pem

echo "✓ Proxy environment configured"
echo "  HTTPS_PROXY=$HTTPS_PROXY"
echo "  NODE_EXTRA_CA_CERTS=$NODE_EXTRA_CA_CERTS"
echo ""
echo "Now run: claude \"your prompt\""
