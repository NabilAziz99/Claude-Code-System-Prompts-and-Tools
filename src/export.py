#!/usr/bin/env python3
"""Export captured Claude Code data to readable text files."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
INPUT_FILE = OUTPUT_DIR / "claude_code_captured.json"


def export_to_txt(output_name: str = None):
    """Export captured data to a readable text file."""
    if not INPUT_FILE.exists():
        print(f"No capture file found: {INPUT_FILE}")
        print("Run Claude through the proxy first.")
        return None

    with open(INPUT_FILE) as f:
        data = json.load(f)

    # Generate output filename with timestamp if not provided
    if output_name is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"capture_{ts}.txt"

    output_file = OUTPUT_DIR / output_name

    lines = []
    lines.append("=" * 80)
    lines.append("CLAUDE CODE API REQUEST CAPTURE")
    lines.append(f"Exported: {datetime.now().isoformat()}")
    lines.append("=" * 80)
    lines.append("")

    # Basic info
    lines.append("-" * 80)
    lines.append("BASIC INFO")
    lines.append("-" * 80)
    lines.append(f"Timestamp:    {data.get('timestamp', 'N/A')}")
    lines.append(f"Endpoint:     {data.get('endpoint', 'N/A')}")
    lines.append(f"Model:        {data.get('model', 'N/A')}")
    lines.append(f"Max Tokens:   {data.get('max_tokens', 'N/A')}")
    lines.append(f"Messages:     {data.get('message_count', 'N/A')}")
    lines.append("")

    # System prompt
    system = data.get("system_prompt")
    lines.append("-" * 80)
    lines.append("SYSTEM PROMPT")
    lines.append("-" * 80)
    if system:
        if isinstance(system, list):
            for i, item in enumerate(system):
                if isinstance(item, dict):
                    if "text" in item:
                        lines.append(f"\n[Block {i+1} - type: {item.get('type', 'text')}]")
                        lines.append(item["text"])
                    else:
                        lines.append(f"\n[Block {i+1}]")
                        lines.append(json.dumps(item, indent=2))
                else:
                    lines.append(str(item))
        elif isinstance(system, str):
            lines.append(system)
        else:
            lines.append(json.dumps(system, indent=2))
    else:
        lines.append("(No system prompt)")
    lines.append("")

    # Tools
    tools = data.get("tools", [])
    lines.append("-" * 80)
    lines.append(f"TOOLS ({len(tools)} total)")
    lines.append("-" * 80)

    for i, tool in enumerate(tools, 1):
        name = tool.get("name", "unknown")
        desc = tool.get("description", "No description")
        params = tool.get("parameters", {})

        lines.append("")
        lines.append(f"{'='*40}")
        lines.append(f"TOOL {i}: {name}")
        lines.append(f"{'='*40}")
        lines.append("")
        lines.append("DESCRIPTION:")
        lines.append(desc)
        lines.append("")
        lines.append("PARAMETERS SCHEMA:")
        lines.append(json.dumps(params, indent=2))

    lines.append("")
    lines.append("=" * 80)
    lines.append("END OF CAPTURE")
    lines.append("=" * 80)

    # Write to file
    with open(output_file, "w") as f:
        f.write("\n".join(lines))

    # Get file size
    size = output_file.stat().st_size
    if size > 1024 * 1024:
        size_str = f"{size / (1024*1024):.1f} MB"
    elif size > 1024:
        size_str = f"{size / 1024:.1f} KB"
    else:
        size_str = f"{size} bytes"

    print(f"Exported to: {output_file}")
    print(f"File size: {size_str}")

    return output_file


def view_summary():
    """Print a summary of the captured data."""
    if not INPUT_FILE.exists():
        print(f"No capture file found: {INPUT_FILE}")
        return

    with open(INPUT_FILE) as f:
        data = json.load(f)

    print("\n" + "=" * 60)
    print("CAPTURED CLAUDE CODE REQUEST")
    print("=" * 60)

    print(f"\nTimestamp: {data.get('timestamp', 'N/A')}")
    print(f"Endpoint:  {data.get('endpoint', 'N/A')}")
    print(f"Model:     {data.get('model', 'N/A')}")
    print(f"Max Tokens: {data.get('max_tokens', 'N/A')}")
    print(f"Messages:  {data.get('message_count', 'N/A')}")

    system = data.get("system_prompt")
    if system:
        system_str = json.dumps(system) if isinstance(system, (list, dict)) else str(system)
        print(f"System:    {len(system_str):,} chars")

    tools = data.get("tools", [])
    print(f"Tools:     {len(tools)}")

    if tools:
        print("\nAvailable Tools:")
        for i, tool in enumerate(tools, 1):
            print(f"  {i:2}. {tool.get('name', 'unknown')}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help"]:
            print("Usage: python export.py [OPTIONS]")
            print("")
            print("Options:")
            print("  -s, --summary    Show summary only (don't export)")
            print("  -o, --output     Specify output filename")
            print("  -h, --help       Show this help")
        elif sys.argv[1] in ["-s", "--summary"]:
            view_summary()
        elif sys.argv[1] in ["-o", "--output"] and len(sys.argv) > 2:
            export_to_txt(sys.argv[2])
        else:
            export_to_txt()
    else:
        export_to_txt()
