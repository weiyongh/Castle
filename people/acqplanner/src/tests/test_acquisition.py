"""
author: Planner
version: 0.6
create_time: 2026-09-16 20:53 +0800
update_time: 2026-09-17 01:20 +0800
status: DRAFT
"""

import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "acquisition.py"
SPEC = importlib.util.spec_from_file_location("acquisition", MODULE_PATH)
acquisition = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(acquisition)


def sample_data():
    return {
        "schema_version": 1,
        "artifact_metadata": {
            "author": "Planner",
            "version": "0.1",
            "create_time": "2026-09-16 20:53 +0800",
            "update_time": "2026-09-17 00:39 +0800",
            "status": "DRAFT",
        },
        "number": "001",
        "l3_name": "慢充",
        "content": "控制主线采集",
        "steps": [
            {"time_s": 0, "speech": "开始采集", "notes": ["充电枪未连接"]},
            {"time_s": 30, "speech": "插枪", "notes": ["等待自然建立充电"]},
            {"time_s": 60, "speech": "停止采集", "notes": ["保存并核对本次采集文件"]},
        ],
        "guide_sections": [{"heading": "执行条件", "items": ["使用正常可用的交流充电设施。"]}],
    }


class AcquisitionTests(unittest.TestCase):
    def test_render_is_stable_and_has_no_script_header(self):
        base, script, guide = acquisition.render_outputs(sample_data())
        self.assertEqual(base, "001-慢充-控制主线采集")
        self.assertTrue(script.startswith("00s     开始采集\n"))
        self.assertTrue(script.rstrip().endswith("保存并核对本次采集文件"))
        self.assertNotIn("操作时间", script)
        self.assertTrue(script.endswith("\n"))
        self.assertIn("author: Planner", guide)
        self.assertIn("status: DRAFT", guide)
        self.assertIn("# 001-慢充-控制主线采集 说明", guide)

    def test_rejects_brand_specific_content(self):
        data = sample_data()
        data["steps"][1]["notes"] = ["在 Tesla App 中操作"]
        with self.assertRaises(acquisition.AcquisitionError):
            acquisition.render_outputs(data)

    def test_rejects_non_increasing_time(self):
        data = sample_data()
        data["steps"][1]["time_s"] = 0
        with self.assertRaises(acquisition.AcquisitionError):
            acquisition.render_outputs(data)

    def test_rejects_time_above_maximum(self):
        data = sample_data()
        data["steps"][-1]["time_s"] = 10000
        with self.assertRaisesRegex(acquisition.AcquisitionError, "9999"):
            acquisition.render_outputs(data)

    def test_rejects_windows_unsafe_name(self):
        data = sample_data()
        data["content"] = "控制:主线"
        with self.assertRaises(acquisition.AcquisitionError):
            acquisition.render_outputs(data)

    def test_requires_starting_acquisition_at_00s(self):
        data = sample_data()
        data["steps"][0]["speech"] = "确认初始状态"
        with self.assertRaisesRegex(acquisition.AcquisitionError, "00s"):
            acquisition.render_outputs(data)

    def test_rejects_second_start_event(self):
        data = sample_data()
        data["steps"][1]["speech"] = "开始采集"
        with self.assertRaisesRegex(acquisition.AcquisitionError, "only"):
            acquisition.render_outputs(data)

    def test_rejects_event_after_stop(self):
        data = sample_data()
        data["steps"].append({"time_s": 90, "speech": "保存文件", "notes": []})
        with self.assertRaisesRegex(acquisition.AcquisitionError, "停止采集"):
            acquisition.render_outputs(data)

    def test_allows_wrap_up_notes_under_final_stop(self):
        _, script, _ = acquisition.render_outputs(sample_data())
        self.assertIn("60s     停止采集\n        保存并核对本次采集文件\n", script)

    def test_event_and_note_text_are_aligned_for_all_time_widths(self):
        data = sample_data()
        data["steps"] = [
            {"time_s": 0, "speech": "开始采集", "notes": ["两位秒数"]},
            {"time_s": 150, "speech": "三位秒数", "notes": []},
            {"time_s": 9999, "speech": "停止采集", "notes": ["四位秒数"]},
        ]
        _, script, _ = acquisition.render_outputs(data)
        for line in script.splitlines():
            if line:
                self.assertNotEqual(line[8], " ")
        self.assertEqual(acquisition.validate_script_shape(script, Path("aligned.txt")), [])

    def test_rendered_files_pass_validation(self):
        data = sample_data()
        base, script, guide = acquisition.render_outputs(data)
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)
            script_path, guide_path = acquisition.output_paths(base, output_dir)
            acquisition.write_lf(script_path, script)
            acquisition.write_lf(guide_path, guide)
            self.assertEqual(acquisition.validate_text(script_path, script), [])
            self.assertEqual(acquisition.validate_text(guide_path, guide), [])
            self.assertEqual(acquisition.validate_script_shape(script, script_path), [])


if __name__ == "__main__":
    unittest.main()
