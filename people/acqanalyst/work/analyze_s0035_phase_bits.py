"""Find raw CAN bit plateaus matching S0035 physical phases.

Artifact Metadata
author: Analyst
version: 0.1
create_time: 2026-09-17
update_time: 2026-09-17
status: DRAFT
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path


ASC = Path(
    "/Users/hwy/Castle_Ranch/acq_baseline/TESLA-M3-SOP5/"
    "001-慢充-控制主线采集_2__20260917_132348_155__S0035/"
    "can/can_20260917132305.asc"
)
OUT = Path("/Users/hwy/Castle/people/acqanalyst/work/analysis_s0035/raw_can")
FRAME = re.compile(
    r"^\s*(\d+(?:\.\d+)?)\s+\d+\s+([0-9A-Fa-f]+)\s+\w+\s+d\s+(\d+)\s*(.*)$"
)
PHASES = {
    "A_pre_plug": (0.0, 8.0),
    "B_plugged_pre_charge": (18.0, 38.0),
    "C_charging_stable": (70.0, 240.0),
    "D_stopped_connected": (270.0, 335.0),
    "E_unlocked_connected": (347.0, 352.0),
    "F_unplugged": (365.0, 395.0),
}


def read_frames() -> dict[int, list[tuple[float, bytes]]]:
    frames: dict[int, list[tuple[float, bytes]]] = defaultdict(list)
    with ASC.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            match = FRAME.match(line)
            if not match:
                continue
            time_s, can_id, dlc, tail = match.groups()
            tokens = tail.split()[: int(dlc)]
            if len(tokens) != int(dlc):
                continue
            frames[int(can_id, 16)].append(
                (float(time_s), bytes(int(token, 16) for token in tokens))
            )
    return frames


def fraction(items: list[tuple[float, bytes]], byte: int, bit: int, lo: float, hi: float):
    values = [(payload[byte] >> bit) & 1 for time_s, payload in items if lo <= time_s < hi and byte < len(payload)]
    return (sum(values) / len(values), len(values)) if values else (None, 0)


def stable(value: float | None) -> bool:
    return value is not None and (value <= 0.05 or value >= 0.95)


def opposite(left: float, right: float) -> bool:
    return abs(left - right) >= 0.90


def transitions(items: list[tuple[float, bytes]], byte: int, bit: int) -> list[dict[str, float | int]]:
    result = []
    previous = None
    for time_s, payload in items:
        if byte >= len(payload):
            continue
        value = (payload[byte] >> bit) & 1
        if previous is not None and value != previous:
            result.append({"time_s": time_s, "from": previous, "to": value})
        previous = value
    return result


def main() -> None:
    frames = read_frames()
    charge_candidates = []
    plug_candidates = []
    unlock_candidates = []
    for can_id, items in frames.items():
        dlc = max(len(payload) for _, payload in items)
        for byte in range(dlc):
            for bit in range(8):
                phase = {}
                counts = {}
                for name, (lo, hi) in PHASES.items():
                    phase[name], counts[name] = fraction(items, byte, bit, lo, hi)
                if not all(counts[name] >= 3 and stable(phase[name]) for name in PHASES):
                    continue
                a, b, c, d, e, f = (phase[name] for name in PHASES)
                record = {
                    "can_id": f"0x{can_id:03X}",
                    "byte": byte,
                    "bit_lsb0": bit,
                    "phase_one_fraction": phase,
                    "phase_frames": counts,
                    "transitions": transitions(items, byte, bit),
                }
                if opposite(c, b) and opposite(c, d) and abs(b - d) <= 0.05:
                    charge_candidates.append(record)
                if opposite(b, a) and opposite(c, a) and opposite(d, f) and opposite(e, f) and abs(a - f) <= 0.05:
                    plug_candidates.append(record)
                if opposite(e, d) and abs(e - f) <= 0.05:
                    unlock_candidates.append(record)
    result = {
        "phases": PHASES,
        "charge_plateau_candidates": charge_candidates,
        "plug_plateau_candidates": plug_candidates,
        "unlock_plateau_candidates": unlock_candidates,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / "phase_bit_candidates.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "charge": len(charge_candidates),
        "plug": len(plug_candidates),
        "unlock": len(unlock_candidates),
        "output": str(target),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
