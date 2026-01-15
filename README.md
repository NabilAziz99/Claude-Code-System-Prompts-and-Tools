# Claude Code Proxy

A tool to capture and inspect Claude Code API requests, including system prompts, tools, and message context.

## Prerequisites

```bash
pip install mitmproxy
```

Run `mitmdump --version` once to generate the CA certificate in `~/.mitmproxy/`.

## Project Structure

```
claude_proxy/
├── run.sh          # Main runner script
├── env.sh          # Environment setup (source this)
├── README.md       # This file
├── src/
│   ├── capture.py  # mitmproxy capture script
│   └── export.py   # Export to readable text
└── output/         # Captured data goes here
    ├── claude_code_captured.json   # Latest capture (raw)
    ├── claude_code_log.jsonl       # History log
    └── capture_*.txt               # Exported readable files
```

## Quick Start

### Terminal 1 - Start the proxy:
```bash
./run.sh proxy
```

### Terminal 2 - Run Claude through the proxy:
```bash
source env.sh
claude "hello"
```

### Terminal 2 - View the captured data:
```bash
./run.sh summary    # Quick summary
./run.sh export     # Export to readable .txt
./run.sh view       # Export and open in editor
```

## Commands

| Command | Description |
|---------|-------------|
| `./run.sh proxy` | Start the mitmproxy server |
| `./run.sh setup` | Print environment variables to set |
| `./run.sh summary` | Show summary of captured data |
| `./run.sh export` | Export to readable text file |
| `./run.sh view` | Export and open in text editor |
| `./run.sh clean` | Remove all captured data |
| `./run.sh help` | Show help message |

## What Gets Captured

- **Model**: The Claude model being used
- **System Prompt**: Full system instructions sent to Claude
- **Tools**: All available tools with their JSON schemas
- **Message Count**: Number of messages in the conversation context
- **Max Tokens**: Token limit for the response

## Output Files

| File | Description |
|------|-------------|
| `output/claude_code_captured.json` | Raw JSON of the latest capture |
| `output/claude_code_log.jsonl` | Append-only log of all captures |
| `output/capture_*.txt` | Human-readable exports |

## Manual Usage

If you prefer not to use the runner script:

```bash
# Terminal 1: Start proxy
mitmdump -s src/capture.py --listen-port 8080

# Terminal 2: Set environment and run Claude
export HTTPS_PROXY=http://127.0.0.1:8080
export HTTP_PROXY=http://127.0.0.1:8080
export NODE_EXTRA_CA_CERTS=~/.mitmproxy/mitmproxy-ca-cert.pem
claude "your prompt"

# View results
python3 src/export.py --summary
python3 src/export.py
```

## How It Works

1. **mitmproxy** acts as a man-in-the-middle proxy
2. Claude Code is configured to route traffic through the proxy
3. The `NODE_EXTRA_CA_CERTS` environment variable makes Node.js trust the proxy's certificate
4. The `capture.py` script intercepts requests to `api.anthropic.com` and extracts relevant data
5. Data is saved to JSON and can be exported to human-readable format

## Troubleshooting

### "Certificate error" or "Connection refused"
- Make sure the proxy is running (`./run.sh proxy`)
- Ensure `~/.mitmproxy/mitmproxy-ca-cert.pem` exists
- Re-run `mitmdump --version` to regenerate certificates

### "No capture found"
- Make sure you ran Claude while the proxy was active
- Check that environment variables are set: `echo $HTTPS_PROXY`

### Port 8080 already in use
- Find what's using it: `lsof -i :8080`
- Kill it or use a different port in `src/capture.py` and `env.sh`
