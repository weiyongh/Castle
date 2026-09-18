"""Run Castle acquisition validation with parent-directory Vehicle identity.

Artifact Metadata
author: Analyst
version: 0.1
create_time: 2026-09-17
update_time: 2026-09-17
status: DRAFT

This compatibility entry point leaves Castle-Tools unchanged. It accepts the
legacy empty Vehicle Marker in the Round directory, or (when that marker is
absent) uses the Round directory's immediate parent name as the Vehicle ID.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path
from typing import Any


TOOL_PATH = Path(
    "/Users/hwy/Castle/tools/acquisition_validate/src/acquisition_context.py"
)
VEHICLE_ID_RE = re.compile(r"^[^-]+-[^-]+-[^-]+$")


def _load_tool() -> Any:
    spec = importlib.util.spec_from_file_location(
        "castle_acquisition_context", TOOL_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load Castle tool: {TOOL_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    tool = _load_tool()
    original_inspect_package = tool.inspect_package

    def inspect_package(package_dir: str | Path) -> dict[str, Any]:
        package = Path(package_dir).resolve()
        try:
            return original_inspect_package(package)
        except tool.AcquisitionContextError as exc:
            expected_error = (
                "vehicle marker: expected one empty extensionless file, found 0"
            )
            if str(exc) != expected_error:
                raise

        vehicle_id = package.parent.name
        if not VEHICLE_ID_RE.fullmatch(vehicle_id):
            raise tool.AcquisitionContextError(
                "vehicle identity: no Round marker and parent directory is not "
                f"MANUFACTURER-MODEL-TECH_VERSION: {vehicle_id!r}"
            )

        info = {
            "package_dir": package,
            "session_path": package / "session.json",
            "csv_path": package / "event_timeline.csv",
            # The parent directory is the authoritative identity source under
            # the revised convention. The original builder only needs .name
            # and stat information from this entry.
            "vehicle_marker": package.parent,
            "photo_files": sorted(
                path for path in (package / "photos").glob("*") if path.is_file()
            ) if (package / "photos").is_dir() else [],
            "audio_files": sorted(
                path for path in (package / "audio").glob("*") if path.is_file()
            ) if (package / "audio").is_dir() else [],
            "asc_files": sorted(
                path for path in (package / "can").glob("*.asc") if path.is_file()
            ) if (package / "can").is_dir() else [],
        }
        missing = [
            path.name
            for path in (info["session_path"], info["csv_path"])
            if not path.is_file()
        ]
        if missing:
            raise tool.AcquisitionContextError(
                f"package missing required files: {missing}"
            )
        return info

    original_fingerprint = tool._fingerprint

    def fingerprint(path: Path, package_dir: Path) -> dict[str, Any]:
        if path == package_dir.parent:
            return {
                "path": "..",
                "kind": "vehicle-parent-directory",
                "vehicle_id": path.name,
            }
        return original_fingerprint(path, package_dir)

    original_verify_fingerprints = tool._verify_fingerprints

    def verify_fingerprints(context: dict[str, Any]) -> None:
        source_files = context.get("package", {}).get("source_files", [])
        vehicle_entries = [
            item for item in source_files
            if item.get("kind") == "vehicle-parent-directory"
        ]
        if len(vehicle_entries) != 1:
            original_verify_fingerprints(context)
            return
        package_path = Path(context["package"]["path"])
        entry = vehicle_entries[0]
        if package_path.parent.name != entry.get("vehicle_id"):
            raise tool.AcquisitionContextError("source changed: Vehicle parent")
        without_vehicle = {
            **context,
            "package": {
                **context["package"],
                "source_files": [
                    item for item in source_files if item is not entry
                ],
            },
        }
        original_verify_fingerprints(without_vehicle)

    tool.inspect_package = inspect_package
    tool._fingerprint = fingerprint
    tool._verify_fingerprints = verify_fingerprints
    return tool.main(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
