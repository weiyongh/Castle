#!/usr/bin/env python3
"""Deterministically sync maintained Notion pages into Castle Assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


TOOL_VERSION = "1.0.0"
NOTION_VERSION = "2022-06-28"
DEFAULT_ASSET_ROOT = Path(__file__).resolve().parents[3] / "assets"


@dataclass(frozen=True)
class Note:
    key: str
    aliases: Tuple[str, ...]
    source_url: str
    page_id: str
    asset_path: Path


NOTES: Tuple[Note, ...] = (
    Note(
        key="新能源汽修L3学习",
        aliases=("L3", "L3笔记", "新能源汽修L3学习"),
        source_url="https://app.notion.com/p/L3-2faa4e43864980399f2cebb011f5f302",
        page_id="2faa4e43-8649-8039-9f2c-ebb011f5f302",
        asset_path=Path("l3-knowledge") / "新能源汽修L3学习",
    ),
)


class SyncError(RuntimeError):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def safe_name(value: str, fallback: str = "untitled") -> str:
    value = re.sub(r"[\\/:*?\"<>|\x00-\x1f]", "-", value).strip().strip(".")
    return value[:120] or fallback


def rich_text(items: Iterable[Dict[str, Any]]) -> str:
    return "".join(str(item.get("plain_text", "")) for item in items)


def page_title(page: Dict[str, Any]) -> str:
    for prop in page.get("properties", {}).values():
        if prop.get("type") == "title":
            title = rich_text(prop.get("title", []))
            if title:
                return title
    return "Untitled"


class NotionClient:
    def __init__(self, token: str, timeout: int = 30) -> None:
        self.token = token
        self.timeout = timeout

    def _json(self, path: str) -> Dict[str, Any]:
        request = urllib.request.Request(
            "https://api.notion.com/v1" + path,
            headers={
                "Authorization": "Bearer " + self.token,
                "Notion-Version": NOTION_VERSION,
                "User-Agent": "Castle-Notioner/" + TOOL_VERSION,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise SyncError(f"Notion API returned HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise SyncError(f"Cannot reach Notion API: {exc.reason}") from exc

    def page(self, page_id: str) -> Dict[str, Any]:
        return self._json("/pages/" + page_id)

    def children(self, block_id: str) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        cursor: Optional[str] = None
        while True:
            query = "?page_size=100"
            if cursor:
                query += "&start_cursor=" + urllib.parse.quote(cursor)
            payload = self._json(f"/blocks/{block_id}/children{query}")
            results.extend(payload.get("results", []))
            if not payload.get("has_more"):
                return results
            cursor = payload.get("next_cursor")
            if not cursor:
                raise SyncError("Notion pagination reported more results without a cursor")

    def download(self, url: str, target: Path) -> None:
        request = urllib.request.Request(url, headers={"User-Agent": "Castle-Notioner/" + TOOL_VERSION})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response, target.open("wb") as output:
                shutil.copyfileobj(response, output)
        except (urllib.error.HTTPError, urllib.error.URLError, OSError) as exc:
            raise SyncError(f"Failed to download attachment {url}: {exc}") from exc


class Exporter:
    def __init__(self, client: NotionClient, root: Path, note: Note) -> None:
        self.client = client
        self.root = root
        self.note = note
        self.pages_dir = root / "pages"
        self.media_dir = root / "media"
        self.raw_pages: List[Dict[str, Any]] = []
        self.block_count = 0
        self.file_count = 0
        self._seen_pages: set[str] = set()

    def export(self) -> Dict[str, Any]:
        self.pages_dir.mkdir(parents=True)
        self.media_dir.mkdir(parents=True)
        root_page, root_markdown = self._export_page(self.note.page_id, is_root=True)
        (self.root / "README.md").write_text(root_markdown, encoding="utf-8")
        raw = {
            "source": self.note.source_url,
            "root_page_id": self.note.page_id,
            "pages": self.raw_pages,
        }
        (self.root / "notion-export.json").write_text(
            json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        manifest = {
            "schema_version": "1.0",
            "tool_version": TOOL_VERSION,
            "notion_api_version": NOTION_VERSION,
            "note": self.note.key,
            "source_url": self.note.source_url,
            "root_page_id": self.note.page_id,
            "root_title": page_title(root_page),
            "synced_at": utc_now().isoformat(),
            "page_count": len(self.raw_pages),
            "block_count": self.block_count,
            "attachment_count": self.file_count,
        }
        (self.root / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        manifest["files"] = file_inventory(self.root)
        (self.root / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        return manifest

    def _export_page(self, page_id: str, is_root: bool = False) -> Tuple[Dict[str, Any], str]:
        normalized = page_id.replace("-", "")
        if normalized in self._seen_pages:
            return {}, ""
        self._seen_pages.add(normalized)
        page = self.client.page(page_id)
        blocks = self._walk_blocks(page_id)
        self.raw_pages.append({"page": page, "blocks": blocks})
        title = page_title(page)
        lines = [f"# {title}", "", f"> 来源：{page.get('url') or self.note.source_url}", ""]
        lines.extend(self._render_blocks(blocks, 0))
        markdown = "\n".join(lines).rstrip() + "\n"
        if not is_root:
            filename = safe_name(title) + "--" + normalized[-8:] + ".md"
            (self.pages_dir / filename).write_text(markdown, encoding="utf-8")
        return page, markdown

    def _walk_blocks(self, block_id: str) -> List[Dict[str, Any]]:
        blocks = self.client.children(block_id)
        for block in blocks:
            self.block_count += 1
            if block.get("has_children") and block.get("type") != "child_page":
                block["_children"] = self._walk_blocks(block["id"])
        return blocks

    def _render_blocks(self, blocks: List[Dict[str, Any]], depth: int) -> List[str]:
        lines: List[str] = []
        for block in blocks:
            kind = block.get("type", "unsupported")
            data = block.get(kind, {})
            text = rich_text(data.get("rich_text", []))
            prefix = "  " * depth
            if kind == "paragraph":
                lines.extend([prefix + text, ""])
            elif kind.startswith("heading_"):
                level = kind[-1]
                lines.extend(["#" * int(level) + " " + text, ""])
            elif kind == "bulleted_list_item":
                lines.append(prefix + "- " + text)
            elif kind == "numbered_list_item":
                lines.append(prefix + "1. " + text)
            elif kind == "to_do":
                lines.append(prefix + ("- [x] " if data.get("checked") else "- [ ] ") + text)
            elif kind == "quote":
                lines.extend([prefix + "> " + text, ""])
            elif kind == "callout":
                icon = data.get("icon", {}).get("emoji", "")
                lines.extend([prefix + "> " + (icon + " " if icon else "") + text, ""])
            elif kind == "toggle":
                lines.extend([prefix + "<details><summary>" + text + "</summary>", ""])
            elif kind == "code":
                language = data.get("language", "")
                lines.extend([f"```{language}", text, "```", ""])
            elif kind == "equation":
                lines.extend(["$$", str(data.get("expression", "")), "$$", ""])
            elif kind == "divider":
                lines.extend(["---", ""])
            elif kind == "child_page":
                child_title = str(data.get("title", "Untitled"))
                self._export_page(block["id"])
                filename = safe_name(child_title) + "--" + block["id"].replace("-", "")[-8:] + ".md"
                lines.extend([f"- [{child_title}](pages/{urllib.parse.quote(filename)})", ""])
            elif kind in {"image", "file", "pdf", "video", "audio"}:
                label, target = self._save_asset(kind, data, block["id"])
                marker = "!" if kind == "image" else ""
                lines.extend([f"{marker}[{label}]({target})", ""])
            elif kind in {"bookmark", "embed", "link_preview"}:
                url = str(data.get("url", ""))
                lines.extend([f"[{url}]({url})", ""])
            elif kind == "table_row":
                cells = [rich_text(cell).replace("|", "\\|") for cell in data.get("cells", [])]
                lines.append("| " + " | ".join(cells) + " |")
            elif kind not in {"table", "synced_block", "column_list", "column", "breadcrumb", "table_of_contents"}:
                lines.extend([f"<!-- Unsupported Notion block: {kind} -->", ""])
            children = block.get("_children", [])
            if children:
                lines.extend(self._render_blocks(children, depth + 1))
                if kind == "toggle":
                    lines.extend([prefix + "</details>", ""])
        return lines

    def _save_asset(self, kind: str, data: Dict[str, Any], block_id: str) -> Tuple[str, str]:
        source = data.get("file") or data.get("external") or {}
        url = source.get("url")
        caption = rich_text(data.get("caption", [])) or kind
        if not url:
            return caption, ""
        basename = Path(urllib.parse.urlparse(url).path).name
        name = safe_name(urllib.parse.unquote(basename), kind)
        if "." not in name:
            name += {"image": ".img", "pdf": ".pdf"}.get(kind, ".bin")
        target = self.media_dir / (block_id.replace("-", "")[-8:] + "-" + name)
        self.client.download(url, target)
        self.file_count += 1
        return caption, "media/" + urllib.parse.quote(target.name)


def file_inventory(root: Path) -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            data = path.read_bytes()
            result.append({
                "path": path.relative_to(root).as_posix(),
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            })
    return result


def resolve_note(value: str) -> Note:
    folded = value.casefold().replace(" ", "")
    for note in NOTES:
        names = (note.key,) + note.aliases
        if folded in {name.casefold().replace(" ", "") for name in names}:
            return note
    known = ", ".join(note.key for note in NOTES)
    raise SyncError(f"Unknown note {value!r}; maintained notes: {known}")


def publish(stage: Path, note_root: Path, operation: str) -> Optional[Path]:
    current = note_root / "current"
    history = note_root / "history"
    history.mkdir(parents=True, exist_ok=True)
    if operation == "download" and current.exists() and any(current.iterdir()):
        raise SyncError(f"Initial download refused: {current} already contains a version; use update")
    archived: Optional[Path] = None
    if current.exists():
        stamp = utc_now().strftime("%Y%m%dT%H%M%SZ")
        archived = history / stamp
        suffix = 1
        while archived.exists():
            archived = history / f"{stamp}-{suffix}"
            suffix += 1
        current.rename(archived)
    try:
        stage.rename(current)
    except Exception:
        if archived and archived.exists() and not current.exists():
            archived.rename(current)
        raise
    return archived


def sync(note: Note, operation: str, asset_root: Path, token: str) -> Dict[str, Any]:
    note_root = asset_root / note.asset_path
    note_root.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".sync-", dir=str(note_root)))
    try:
        manifest = Exporter(NotionClient(token), stage, note).export()
        archived = publish(stage, note_root, operation)
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise
    return {
        "status": "success",
        "operation": operation,
        "note": note.key,
        "current": str(note_root / "current"),
        "archived": str(archived) if archived else None,
        "page_count": manifest["page_count"],
        "block_count": manifest["block_count"],
        "attachment_count": manifest["attachment_count"],
    }


def import_export(note: Note, zip_path: Path, asset_root: Path, operation: str) -> Dict[str, Any]:
    if not zip_path.is_file():
        raise SyncError(f"Notion export ZIP does not exist: {zip_path}")
    note_root = asset_root / note.asset_path
    note_root.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".sync-", dir=str(note_root)))
    try:
        with zipfile.ZipFile(zip_path) as archive:
            members = archive.infolist()
            for member in members:
                path = Path(member.filename)
                mode = member.external_attr >> 16
                if path.is_absolute() or ".." in path.parts:
                    raise SyncError(f"Unsafe path in Notion export: {member.filename}")
                if mode & 0o170000 == 0o120000:
                    raise SyncError(f"Symbolic link is not allowed in Notion export: {member.filename}")
            archive.extractall(stage)
        files = [path for path in stage.rglob("*") if path.is_file()]
        markdown_count = sum(path.suffix.lower() == ".md" for path in files)
        attachment_count = sum(path.suffix.lower() not in {".md", ".csv"} for path in files)
        if markdown_count == 0:
            raise SyncError("Notion export contains no Markdown pages")
        manifest = {
            "schema_version": "1.0",
            "tool_version": TOOL_VERSION,
            "export_mode": "notion-browser-markdown-csv",
            "note": note.key,
            "source_url": note.source_url,
            "root_page_id": note.page_id,
            "synced_at": utc_now().isoformat(),
            "source_archive": zip_path.name,
            "source_archive_sha256": hashlib.sha256(zip_path.read_bytes()).hexdigest(),
            "page_count": markdown_count,
            "attachment_count": attachment_count,
            "files": file_inventory(stage),
        }
        (stage / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        archived = publish(stage, note_root, operation)
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise
    return {
        "status": "success",
        "operation": "import-export",
        "note": note.key,
        "current": str(note_root / "current"),
        "archived": str(archived) if archived else None,
        "page_count": markdown_count,
        "attachment_count": attachment_count,
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("operation", choices=("download", "update", "update-all", "import-export"))
    result.add_argument("note", nargs="?", help="maintained note name or alias")
    result.add_argument("--asset-root", type=Path, default=DEFAULT_ASSET_ROOT)
    result.add_argument("--token-env", default="NOTION_TOKEN")
    result.add_argument("--zip", type=Path, help="Notion Markdown/CSV export ZIP")
    result.add_argument("--as-update", action="store_true", help="archive an existing current version")
    return result


def main(argv: Optional[List[str]] = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.operation == "import-export":
            if not args.note or not args.zip:
                raise SyncError("import-export requires a note name and --zip")
            output = import_export(
                resolve_note(args.note), args.zip, args.asset_root,
                "update" if args.as_update else "download",
            )
        else:
            token = os.environ.get(args.token_env, "").strip()
            if not token:
                print(json.dumps({"status": "error", "error": f"environment variable {args.token_env} is not set"}, ensure_ascii=False), file=sys.stderr)
                return 2
            if args.operation == "update-all":
                if args.note:
                    raise SyncError("update-all does not accept a note name")
                output = [sync(note, "update", args.asset_root, token) for note in NOTES]
            else:
                if not args.note:
                    raise SyncError(f"{args.operation} requires a note name")
                output = sync(resolve_note(args.note), args.operation, args.asset_root, token)
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0
    except SyncError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
