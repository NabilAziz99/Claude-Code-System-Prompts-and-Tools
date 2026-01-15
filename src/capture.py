"""mitmproxy script to capture Claude Code API requests."""

from mitmproxy import http
import json
import os
from datetime import datetime
from pathlib import Path

# Output directory (relative to project root)
OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_FILE = OUTPUT_DIR / "claude_code_captured.json"
LOG_FILE = OUTPUT_DIR / "claude_code_log.jsonl"

def request(flow: http.HTTPFlow) -> None:
    if "api.anthropic.com" not in flow.request.pretty_host:
        return

    if not flow.request.content:
        return

    try:
        body = json.loads(flow.request.content)
    except json.JSONDecodeError:
        return

    # Skip non-message endpoints
    if "messages" not in flow.request.path:
        return

    timestamp = datetime.now().isoformat()

    captured = {
        "timestamp": timestamp,
        "endpoint": flow.request.path,
        "model": body.get("model"),
        "system_prompt": body.get("system"),
        "tools": body.get("tools", []),
        "max_tokens": body.get("max_tokens"),
        "message_count": len(body.get("messages", [])),
    }

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Save latest capture (overwrites)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(captured, f, indent=2)

    # Append to log (keeps history)
    log_entry = {
        "timestamp": timestamp,
        "model": captured["model"],
        "system_chars": len(str(captured["system_prompt"])),
        "tool_count": len(captured["tools"]),
        "message_count": captured["message_count"],
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    tool_count = len(captured["tools"])
    system_len = len(str(captured["system_prompt"]))

    print(f"\n{'='*50}")
    print(f"[{timestamp}] Captured API Request!")
    print(f"  - Endpoint: {captured['endpoint']}")
    print(f"  - Model: {captured['model']}")
    print(f"  - System prompt: {system_len:,} chars")
    print(f"  - Tools: {tool_count}")
    print(f"  - Messages in context: {captured['message_count']}")
    print(f"  - Saved to: {OUTPUT_FILE}")
    print(f"{'='*50}\n")
