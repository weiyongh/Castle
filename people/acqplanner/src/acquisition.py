#!/usr/bin/env python3
# author: Planner
# version: 0.6
# create_time: 2026-09-16 20:53 +0800
# update_time: 2026-09-17 01:20 +0800
# status: DRAFT
"""Deterministically render and validate Acquisition output pairs."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any


NAME_RE = re.compile(r"^(\d{3})-([^-]+)-(.+)$")
TIME_RE = re.compile(r"^(\d+)s( +)(\S.*)$")
MAX_TIME_S = 9999
CONTENT_COLUMN = 8
WINDOWS_UNSAFE_RE = re.compile(r'[<>:"/\\|?*]')
FORBIDDEN_OUTPUT_TERMS = (
    "Tesla",
    "Model 3",
    "特斯拉",
    "奥迪",
    "奔驰",
    "Tesla App",
)
FORBIDDEN_SCRIPT_LINES = ("采集条件", "操作时间", "操作/播报内容")
ARTIFACT_STATUSES = {"DRAFT", "TO_AUDIT", "REJECT", "CONFIRM", "PUBLISH"}
TIME_VALUE_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2} [+-]\d{4}$")


class AcquisitionError(ValueError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise AcquisitionError(f"{path}: UTF-8 BOM is not allowed")
    if b"\r" in raw:
        raise AcquisitionError(f"{path}: use LF line endings")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AcquisitionError(f"{path}: not valid UTF-8") from exc
    if unicodedata.normalize("NFC", text) != text:
        raise AcquisitionError(f"{path}: text must use Unicode NFC")
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise AcquisitionError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise AcquisitionError(f"{path}: root must be an object")
    return value


def require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise AcquisitionError(f"{field}: must be non-empty text without edge whitespace")
    if "\n" in value or "\r" in value or "\t" in value:
        raise AcquisitionError(f"{field}: must be a single line without tabs")
    return unicodedata.normalize("NFC", value)


def validate_source(data: dict[str, Any]) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    if data.get("schema_version") != 1:
        raise AcquisitionError("schema_version must be 1")
    metadata = data.get("artifact_metadata")
    if not isinstance(metadata, dict):
        raise AcquisitionError("artifact_metadata must be an object")
    if require_text(metadata.get("author"), "artifact_metadata.author") != "Planner":
        raise AcquisitionError("artifact_metadata.author must use the Planner signature")
    require_text(metadata.get("version"), "artifact_metadata.version")
    for field in ("create_time", "update_time"):
        value = require_text(metadata.get(field), f"artifact_metadata.{field}")
        if not TIME_VALUE_RE.fullmatch(value):
            raise AcquisitionError(f"artifact_metadata.{field}: use YYYY-MM-DD HH:MM +ZZZZ")
    status = require_text(metadata.get("status"), "artifact_metadata.status")
    if status not in ARTIFACT_STATUSES:
        raise AcquisitionError("artifact_metadata.status is not a Castle status")
    number = require_text(data.get("number"), "number")
    l3_name = require_text(data.get("l3_name"), "l3_name")
    content = require_text(data.get("content"), "content")
    base = f"{number}-{l3_name}-{content}"
    if not NAME_RE.fullmatch(base):
        raise AcquisitionError("number must use three digits and names must be filesystem-safe")
    if WINDOWS_UNSAFE_RE.search(base) or base.endswith((" ", ".")):
        raise AcquisitionError("name contains characters that are unsafe on Windows")

    steps = data.get("steps")
    if not isinstance(steps, list) or not steps:
        raise AcquisitionError("steps must be a non-empty array")
    previous = -1
    normalized_steps: list[dict[str, Any]] = []
    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            raise AcquisitionError(f"steps[{index}]: must be an object")
        seconds = step.get("time_s")
        if not isinstance(seconds, int) or isinstance(seconds, bool) or not 0 <= seconds <= MAX_TIME_S:
            raise AcquisitionError(f"steps[{index}].time_s: must be an integer from 0 to {MAX_TIME_S}")
        if seconds <= previous:
            raise AcquisitionError("step times must be strictly increasing")
        if index == 0 and seconds != 0:
            raise AcquisitionError("the first step must start at 00s")
        previous = seconds
        speech = require_text(step.get("speech"), f"steps[{index}].speech")
        if speech.startswith("播报"):
            raise AcquisitionError(f"steps[{index}].speech: do not prefix speech with ‘播报’")
        notes = step.get("notes", [])
        if not isinstance(notes, list):
            raise AcquisitionError(f"steps[{index}].notes: must be an array")
        normalized_notes = [require_text(note, f"steps[{index}].notes") for note in notes]
        normalized_steps.append({"time_s": seconds, "speech": speech, "notes": normalized_notes})

    start_indexes = [index for index, step in enumerate(normalized_steps) if step["speech"] == "开始采集"]
    if start_indexes != [0]:
        raise AcquisitionError("the 00s event must be the only ‘开始采集’ event")
    if normalized_steps[-1]["speech"] != "停止采集":
        raise AcquisitionError("the final event must be ‘停止采集’")

    sections = data.get("guide_sections")
    if not isinstance(sections, list) or not sections:
        raise AcquisitionError("guide_sections must be a non-empty array")
    normalized_sections: list[dict[str, Any]] = []
    for index, section in enumerate(sections):
        if not isinstance(section, dict):
            raise AcquisitionError(f"guide_sections[{index}]: must be an object")
        heading = require_text(section.get("heading"), f"guide_sections[{index}].heading")
        items = section.get("items")
        if not isinstance(items, list) or not items:
            raise AcquisitionError(f"guide_sections[{index}].items: must be a non-empty array")
        normalized_sections.append(
            {"heading": heading, "items": [require_text(item, f"guide_sections[{index}].items") for item in items]}
        )

    all_text = json.dumps(data, ensure_ascii=False)
    found = [term for term in FORBIDDEN_OUTPUT_TERMS if term.casefold() in all_text.casefold()]
    if found:
        raise AcquisitionError(f"brand/model-specific terms are not allowed: {', '.join(found)}")
    return base, normalized_steps, normalized_sections


def render_outputs(data: dict[str, Any]) -> tuple[str, str, str]:
    base, steps, sections = validate_source(data)
    script_blocks = []
    for step in steps:
        time_field = f"{step['time_s']:02d}s".ljust(5)
        lines = [f"{time_field}   {step['speech']}"]
        lines.extend(f"{' ' * CONTENT_COLUMN}{note}" for note in step["notes"])
        script_blocks.append("\n".join(lines))
    script = "\n\n".join(script_blocks) + "\n"

    metadata = data["artifact_metadata"]
    guide_lines = [
        "---",
        f"author: {metadata['author']}",
        f"version: {metadata['version']}",
        f"create_time: {metadata['create_time']}",
        f"update_time: {metadata['update_time']}",
        f"status: {metadata['status']}",
        "---",
        "",
        f"# {base} 说明",
    ]
    for section in sections:
        guide_lines.extend(["", f"## {section['heading']}", ""])
        guide_lines.extend(f"- {item}" for item in section["items"])
    guide = "\n".join(guide_lines) + "\n"
    if len(guide) > 2000:
        raise AcquisitionError("guide must remain concise (maximum 2000 characters)")
    return base, script, guide


def validate_text(path: Path, expected: str) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"{path}: missing output"]
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        errors.append(f"{path}: UTF-8 BOM is not allowed")
    if b"\r" in raw:
        errors.append(f"{path}: use LF line endings")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return errors + [f"{path}: not valid UTF-8"]
    if "\t" in text:
        errors.append(f"{path}: tabs are not allowed")
    if any(line.endswith(" ") for line in text.splitlines()):
        errors.append(f"{path}: trailing whitespace is not allowed")
    if unicodedata.normalize("NFC", text) != text:
        errors.append(f"{path}: text must use Unicode NFC")
    if text != expected:
        errors.append(f"{path}: output does not match deterministic rendering")
    return errors


def validate_script_shape(text: str, path: Path) -> list[str]:
    errors: list[str] = []
    for forbidden in FORBIDDEN_SCRIPT_LINES:
        if forbidden in text:
            errors.append(f"{path}: script contains forbidden heading/table label: {forbidden}")
    blocks = text.rstrip("\n").split("\n\n")
    previous = -1
    for index, block in enumerate(blocks):
        lines = block.splitlines()
        match = TIME_RE.fullmatch(lines[0]) if lines else None
        if not match:
            errors.append(f"{path}: block {index + 1} has an invalid event line")
            continue
        seconds = int(match.group(1))
        event_prefix_width = len(match.group(1)) + 1 + len(match.group(2))
        if event_prefix_width != CONTENT_COLUMN:
            errors.append(f"{path}: block {index + 1} event text must start in column {CONTENT_COLUMN + 1}")
        if seconds > MAX_TIME_S:
            errors.append(f"{path}: block {index + 1} time must not exceed {MAX_TIME_S}s")
        if seconds <= previous:
            errors.append(f"{path}: event times must be strictly increasing")
        previous = seconds
        for line in lines[1:]:
            if not line.startswith(" " * CONTENT_COLUMN) or line.startswith(" " * (CONTENT_COLUMN + 1)) or not line.strip():
                errors.append(f"{path}: block {index + 1} has an invalid note line")
    return errors


def write_lf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(unicodedata.normalize("NFC", text).encode("utf-8"))


def output_paths(base: str, output_dir: Path) -> tuple[Path, Path]:
    return output_dir / f"{base}.txt", output_dir / f"{base}.md"


def validate_source_name(source: Path, base: str) -> None:
    expected = f"{base}.source.json"
    if source.name != expected:
        raise AcquisitionError(f"source filename must be {expected}")


def command_render(source: Path, output_dir: Path) -> int:
    base, script, guide = render_outputs(read_json(source))
    validate_source_name(source, base)
    script_path, guide_path = output_paths(base, output_dir)
    write_lf(script_path, script)
    write_lf(guide_path, guide)
    print(script_path)
    print(guide_path)
    return 0


def command_check(source: Path, output_dir: Path) -> int:
    base, script, guide = render_outputs(read_json(source))
    validate_source_name(source, base)
    script_path, guide_path = output_paths(base, output_dir)
    errors = validate_text(script_path, script) + validate_text(guide_path, guide)
    if script_path.is_file():
        errors.extend(validate_script_shape(script_path.read_text(encoding="utf-8"), script_path))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: {base}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("render", "check"):
        command = subparsers.add_parser(name)
        command.add_argument("source", type=Path)
        command.add_argument("--output-dir", type=Path, default=Path("work"))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "render":
            return command_render(args.source, args.output_dir)
        return command_check(args.source, args.output_dir)
    except (AcquisitionError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
