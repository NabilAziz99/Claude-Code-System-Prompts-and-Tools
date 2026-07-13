"""mitmproxy script to capture Claude Code API requests."""

from mitmproxy import http
import json
import re
from datetime import datetime
from pathlib import Path

# Output directory (relative to project root)
OUTPUT_DIR = Path(__file__).parent.parent / "output"
CAPTURES_DIR = OUTPUT_DIR / "captures"          # one file per request (never overwritten)
OUTPUT_FILE = OUTPUT_DIR / "claude_code_captured.json"   # latest request (overwritten)
LOG_FILE = OUTPUT_DIR / "claude_code_log.jsonl"


def _request_label(body: dict) -> str:
    """Classify the request so per-request filenames are easy to scan.

    Returns a short slug like 'subagent', 'security-review', 'utility', 'main'.
    """
    system = body.get("system")
    system_str = json.dumps(system) if system is not None else ""
    messages_str = json.dumps(body.get("messages", []))

    # Subagents carry an explicit billing marker in their first system block.
    is_subagent = "cc_is_subagent=true" in system_str

    # The security-review skill injects its instructions as a user message, so
    # only scan the *messages* here. (Scanning the system prompt gives false
    # positives because the standard Claude Code system prompt lists the
    # `security-review` skill in its available-skills section.)
    blob = messages_str.lower()
    if "security review" in blob or "security-review" in blob or "vulnerabilit" in blob:
        return "security-review-subagent" if is_subagent else "security-review"

    if is_subagent:
        return "subagent"

    # Small utility calls (title generation, intent classification) have a tiny
    # system prompt and no tools.
    if len(system_str) < 50 and not body.get("tools"):
        return "utility"

    return "main"


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
    messages = body.get("messages", [])

    captured = {
        "timestamp": timestamp,
        "endpoint": flow.request.path,
        "model": body.get("model"),
        "system_prompt": body.get("system"),
        "tools": body.get("tools", []),
        "max_tokens": body.get("max_tokens"),
        "message_count": len(messages),
        # NEW: keep the full conversation. Slash-command / skill instructions
        # (like /security-review) live here as user messages, not in `system`.
        "messages": messages,
    }

    label = _request_label(body)

    # Ensure output directories exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CAPTURES_DIR.mkdir(parents=True, exist_ok=True)

    # NEW: write one file per request so concurrent calls (main + subagent +
    # utility) no longer clobber each other.
    safe_ts = re.sub(r"[^0-9]", "", timestamp)
    per_request_file = CAPTURES_DIR / f"{safe_ts}_{label}.json"
    with open(per_request_file, "w") as f:
        json.dump(captured, f, indent=2)

    # Keep the "latest request" file for backwards compatibility with export.py
    with open(OUTPUT_FILE, "w") as f:
        json.dump(captured, f, indent=2)

    # Append to log (keeps history)
    log_entry = {
        "timestamp": timestamp,
        "label": label,
        "model": captured["model"],
        "system_chars": len(json.dumps(captured["system_prompt"])) if captured["system_prompt"] else 0,
        "tool_count": len(captured["tools"]),
        "message_count": captured["message_count"],
        "file": per_request_file.name,
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    tool_count = len(captured["tools"])
    system_len = log_entry["system_chars"]

    print(f"\n{'='*50}")
    print(f"[{timestamp}] Captured API Request!  ({label})")
    print(f"  - Endpoint: {captured['endpoint']}")
    print(f"  - Model: {captured['model']}")
    print(f"  - System prompt: {system_len:,} chars")
    print(f"  - Tools: {tool_count}")
    print(f"  - Messages in context: {captured['message_count']}")
    print(f"  - Saved to: {per_request_file}")
    print(f"{'='*50}\n")
