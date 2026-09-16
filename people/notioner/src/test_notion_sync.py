import json
import tempfile
import unittest
import zipfile
from pathlib import Path

import notion_sync


class FakeClient:
    def page(self, page_id):
        return {
            "id": page_id,
            "url": "https://notion.test/" + page_id,
            "properties": {"Name": {"type": "title", "title": [{"plain_text": "测试笔记"}]}},
        }

    def children(self, block_id):
        if block_id == "root":
            return [{
                "id": "block-1",
                "type": "paragraph",
                "has_children": False,
                "paragraph": {"rich_text": [{"plain_text": "正文"}]},
            }]
        return []

    def download(self, url, target):
        target.write_bytes(b"asset")


class SyncTests(unittest.TestCase):
    def test_default_asset_root_is_castle_assets(self):
        self.assertEqual(
            notion_sync.DEFAULT_ASSET_ROOT,
            Path(__file__).resolve().parents[3] / "assets",
        )

    def test_resolve_alias(self):
        self.assertEqual(notion_sync.resolve_note("L3").key, "新能源汽修L3学习")

    def test_export_writes_readable_and_raw_versions(self):
        note = notion_sync.Note("测试", ("T",), "https://notion.test/root", "root", Path("test"))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = notion_sync.Exporter(FakeClient(), root, note).export()
            self.assertIn("正文", (root / "README.md").read_text(encoding="utf-8"))
            self.assertEqual(manifest["page_count"], 1)
            raw = json.loads((root / "notion-export.json").read_text(encoding="utf-8"))
            self.assertEqual(raw["root_page_id"], "root")

    def test_publish_archives_old_current(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            current = root / "current"
            current.mkdir()
            (current / "old.txt").write_text("old")
            stage = root / ".stage"
            stage.mkdir()
            (stage / "new.txt").write_text("new")
            archived = notion_sync.publish(stage, root, "update")
            self.assertEqual((root / "current" / "new.txt").read_text(), "new")
            self.assertEqual((archived / "old.txt").read_text(), "old")

    def test_download_refuses_to_replace_existing_current(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            current = root / "current"
            current.mkdir()
            (current / "old.txt").write_text("old")
            stage = root / ".stage"
            stage.mkdir()
            with self.assertRaises(notion_sync.SyncError):
                notion_sync.publish(stage, root, "download")

    def test_import_browser_export(self):
        note = notion_sync.Note("测试", ("T",), "https://notion.test/root", "root", Path("test"))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "export.zip"
            with zipfile.ZipFile(archive, "w") as output:
                output.writestr("测试 root.md", "# 测试\n")
                output.writestr("测试/image.png", b"png")
            result = notion_sync.import_export(note, archive, root / "assets", "download")
            current = root / "assets" / "test" / "current"
            self.assertEqual(result["page_count"], 1)
            self.assertEqual(result["attachment_count"], 1)
            self.assertTrue((current / "manifest.json").is_file())

    def test_import_rejects_path_traversal(self):
        note = notion_sync.Note("测试", ("T",), "https://notion.test/root", "root", Path("test"))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "bad.zip"
            with zipfile.ZipFile(archive, "w") as output:
                output.writestr("../escape.md", "bad")
            with self.assertRaises(notion_sync.SyncError):
                notion_sync.import_export(note, archive, root / "assets", "download")


if __name__ == "__main__":
    unittest.main()
