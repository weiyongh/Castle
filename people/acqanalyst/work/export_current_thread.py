#!/usr/bin/env python3
"""Export a Codex desktop task's visible conversation to Markdown.

Author: 牛猛 (Acquisition Analyst)
Version: 0.2.0
Created: 2026-09-18
Updated: 2026-09-18
Status: DRAFT

The Codex history database is opened read-only. Only userMessage and
agentMessage records are exported; tool calls, tool outputs, reasoning,
system/developer context, and other internal records are excluded.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


CURRENT_THREAD_ID = "01a0ad35-7bd2-7200-be9e-96bc54f81c8c"
DEFAULT_DB = Path.home() / ".codex" / "thread_history_1.sqlite"
DEFAULT_INDEX = Path.home() / ".codex" / "session_index.jsonl"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export visible Codex task messages to a Markdown file."
    )
    parser.add_argument(
        "--thread-id",
        default=CURRENT_THREAD_ID,
        help=f"task/thread ID (default: current task {CURRENT_THREAD_ID})",
    )
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="history SQLite DB")
    parser.add_argument(
        "--index", type=Path, default=DEFAULT_INDEX, help="session index JSONL"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="output .md path (default: ./<start-time>_<task-title>.md)",
    )
    parser.add_argument(
        "--final-only",
        action="store_true",
        help="omit assistant commentary/progress updates; keep final answers",
    )
    parser.add_argument(
        "--timestamps",
        action="store_true",
        help="add local timestamps to message headings",
    )
    return parser.parse_args()


def load_title(index_path: Path, thread_id: str) -> str:
    title = "Codex conversation"
    try:
        with index_path.open("r", encoding="utf-8") as stream:
            for line in stream:
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if row.get("id") == thread_id and row.get("thread_name"):
                    title = str(row["thread_name"])
    except FileNotFoundError:
        pass
    return title


def safe_title(title: str) -> str:
    cleaned = "".join(
        "_" if char in '/\\:*?\"<>|\n\r\t' else char for char in title
    ).strip(" ._")
    return (cleaned or "codex_conversation")[:100]


def open_read_only(db_path: Path) -> sqlite3.Connection:
    resolved = db_path.expanduser().resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"history database not found: {resolved}")
    return sqlite3.connect(f"file:{resolved}?mode=ro", uri=True)


def extract_user_text(item: dict[str, Any]) -> str:
    parts: list[str] = []
    for block in item.get("content", []):
        if isinstance(block, dict) and block.get("type") == "text":
            text = block.get("text")
            if isinstance(text, str) and text.strip():
                parts.append(text.strip())
    return "\n\n".join(parts)


def iter_messages(
    connection: sqlite3.Connection, thread_id: str, final_only: bool
) -> Iterable[tuple[str, str, int, str | None]]:
    rows = connection.execute(
        """
        SELECT item_type, item_json, created_at_ms
        FROM thread_items
        WHERE thread_id = ? AND item_type IN ('userMessage', 'agentMessage')
        ORDER BY rollout_ordinal, created_at_ms
        """,
        (thread_id,),
    )
    for item_type, raw_json, created_at_ms in rows:
        try:
            item = json.loads(raw_json)
        except (TypeError, json.JSONDecodeError):
            continue

        if item_type == "userMessage":
            text = extract_user_text(item)
            role = "用户"
            phase = None
        else:
            phase = item.get("phase")
            if final_only and phase != "final_answer":
                continue
            text = item.get("text", "")
            role = "助手"

        if isinstance(text, str) and text.strip():
            yield role, text.strip(), int(created_at_ms), phase


def timestamp_text(created_at_ms: int) -> str:
    return datetime.fromtimestamp(created_at_ms / 1000).astimezone().strftime(
        "%Y-%m-%d %H:%M:%S %z"
    )


def filename_timestamp(created_at_ms: int) -> str:
    """Return the conversation start time in local time for filenames."""
    return datetime.fromtimestamp(created_at_ms / 1000).astimezone().strftime(
        "%Y%m%d_%H%M%S"
    )


def conversation_start_ms(connection: sqlite3.Connection, thread_id: str) -> int:
    row = connection.execute(
        """
        SELECT MIN(created_at_ms)
        FROM thread_items
        WHERE thread_id = ? AND item_type IN ('userMessage', 'agentMessage')
        """,
        (thread_id,),
    ).fetchone()
    if not row or row[0] is None:
        raise ValueError(f"no visible messages found for {thread_id}")
    return int(row[0])


def render_markdown(
    title: str,
    thread_id: str,
    messages: Iterable[tuple[str, str, int, str | None]],
    timestamps: bool,
) -> tuple[str, int]:
    lines = [f"# {title}", "", f"- Task ID: `{thread_id}`", ""]
    count = 0
    for role, text, created_at_ms, phase in messages:
        count += 1
        suffix = f" · {timestamp_text(created_at_ms)}" if timestamps else ""
        phase_label = "（过程更新）" if phase == "commentary" else ""
        lines.extend([f"## {role}{phase_label}{suffix}", "", text, ""])
    return "\n".join(lines).rstrip() + "\n", count


def main() -> int:
    args = parse_args()
    title = load_title(args.index.expanduser(), args.thread_id)

    try:
        with open_read_only(args.db) as connection:
            start_ms = conversation_start_ms(connection, args.thread_id)
            markdown, count = render_markdown(
                title,
                args.thread_id,
                iter_messages(connection, args.thread_id, args.final_only),
                args.timestamps,
            )
    except (FileNotFoundError, sqlite3.Error, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if count == 0:
        print(f"error: no visible messages found for {args.thread_id}", file=sys.stderr)
        return 2

    default_name = f"{filename_timestamp(start_ms)}_{safe_title(title)}.md"
    output = (args.output or Path.cwd() / default_name).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(markdown, encoding="utf-8")
    print(f"exported {count} messages to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
