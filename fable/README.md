# Fable (`claude-fable-5`) — Captured System Prompt & Tools

This folder holds what Claude Code actually sends to Anthropic's API when you run it
against the **Fable 5** model (`claude-fable-5`), captured with the mitmproxy in this
repo.

| File | What it is |
|------|------------|
| [`system-prompt.md`](system-prompt.md) | The full system prompt Claude Code sent to Fable (billing header block stripped). |
| [`tools.md`](tools.md) | Human-readable list of every tool + its JSON schema. |
| [`tools.json`](tools.json) | Raw `tools` array exactly as sent to the API. |
| [`raw-capture.json`](raw-capture.json) | The complete intercepted request (model, system, tools, messages, max_tokens). |

## Capture details

- **Model:** `claude-fable-5`
- **Claude Code version:** 2.1.193
- **Endpoint:** `POST /v1/messages?beta=true`
- **max_tokens:** 64000
- **Captured:** 2026-07-13
- **Mode:** headless / print mode (`claude -p`). In this mode Claude Code sends a
  **deferred tool set** — only 9 core tools are sent up front (`Agent`, `Bash`,
  `Edit`, `Read`, `ScheduleWakeup`, `Skill`, `ToolSearch`, `Workflow`, `Write`) and
  the rest are pulled in on demand via `ToolSearch`.

## How this was captured

```bash
# Terminal 1 — start the intercepting proxy
./run.sh proxy

# Terminal 2 — route Claude Code (on the Fable model) through it
source env.sh
claude --model claude-fable-5 -p "say hi in one word"

# Then regenerate this folder from the newest capture
python3 src/export.py            # readable dump of the latest request
```

The system prompt is model-agnostic Claude Code scaffolding — selecting `claude-fable-5`
changes which model receives it, not the prompt text itself. Re-run the capture to refresh
after a Claude Code upgrade.
