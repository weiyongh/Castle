"""Evidence-first raw CAN exploration for Castle Round S0035.

Artifact Metadata
author: Analyst
version: 0.1
create_time: 2026-09-17
update_time: 2026-09-17
status: DRAFT

This program deliberately performs no DBC decoding. It finds raw CAN bits
whose prevalence changes across independently recorded Event clocks and frame
IDs whose rate changes across those same windows.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


PACKAGE = Path(
    "/Users/hwy/Castle_Ranch/acq_baseline/TESLA-M3-SOP5/"
    "001-慢充-控制主线采集_2__20260917_132348_155__S0035"
)
ASC = PACKAGE / "can/can_20260917132305.asc"
TIMELINE = PACKAGE / "event_timeline.csv"
OUT = Path(
    "/Users/hwy/Castle/people/acqanalyst/work/analysis_s0035/raw_can"
)

ASC_DATE = re.compile(
    r"^date\s+\w+\s+(\w+)\s+(\d{1,2})\s+(\d{2}):(\d{2}):(\d{2})\s+"
    r"(AM|PM)\s+(\d{4})$",
    re.I,
)
FRAME = re.compile(
    r"^\s*(\d+(?:\.\d+)?)\s+\d+\s+([0-9A-Fa-f]+)\s+\w+\s+d\s+"
    r"(\d+)\s*(.*)$"
)
MONTHS = {
    name: index
    for index, name in enumerate(
        ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"),
        1,
    )
}


def asc_start_clock() -> datetime:
    with ASC.open(encoding="utf-8", errors="replace") as stream:
        header = stream.readline().strip()
    match = ASC_DATE.match(header)
    if not match:
        raise ValueError(f"unsupported ASC date header: {header!r}")
    month, day, hour, minute, second, am_pm, year = match.groups()
    hour_i = int(hour) % 12 + (12 if am_pm.upper() == "PM" else 0)
    # Timeline carries +08:00. Use its tzinfo rather than assuming host locale.
    with TIMELINE.open(encoding="utf-8", newline="") as stream:
        first_clock = next(csv.DictReader(stream))["clock_iso"]
    tz = datetime.fromisoformat(first_clock).tzinfo
    return datetime(
        int(year), MONTHS[month.title()], int(day), hour_i, int(minute), int(second), tzinfo=tz
    )


def event_offsets(start: datetime) -> list[dict[str, object]]:
    result = []
    with TIMELINE.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            if not row["clock_iso"]:
                continue
            result.append(
                {
                    "event_id": row["event_id"],
                    "action": row["action"],
                    "offset_s": (datetime.fromisoformat(row["clock_iso"]) - start).total_seconds(),
                }
            )
    return result


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
            try:
                payload = bytes(int(token, 16) for token in tokens)
            except ValueError:
                continue
            frames[int(can_id, 16)].append((float(time_s), payload))
    return frames


def in_window(items: list[tuple[float, bytes]], lo: float, hi: float) -> list[bytes]:
    return [payload for time_s, payload in items if lo <= time_s < hi]


def bit_prevalence(payloads: list[bytes], dlc: int) -> list[float]:
    if not payloads:
        return []
    return [
        sum((payload[byte] >> bit) & 1 for payload in payloads if len(payload) > byte)
        / sum(1 for payload in payloads if len(payload) > byte)
        for byte in range(dlc)
        for bit in range(8)
    ]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    start = asc_start_clock()
    events = event_offsets(start)
    frames = read_frames()

    inventory = []
    for can_id, items in sorted(frames.items()):
        dlcs = Counter(len(payload) for _, payload in items)
        inventory.append(
            {
                "can_id": f"0x{can_id:03X}",
                "frames": len(items),
                "first_s": items[0][0],
                "last_s": items[-1][0],
                "duration_s": items[-1][0] - items[0][0],
                "mean_hz": len(items) / max(items[-1][0] - items[0][0], 1e-9),
                "dlc_counts": dict(sorted(dlcs.items())),
                "unique_payloads": len({payload for _, payload in items}),
            }
        )

    transitions = []
    rates = []
    # Avoid E01/E02/E11 because they are outside the ASC. E05/E07 are observation
    # events rather than commanded physical transitions, but retain them as checks.
    for event in events:
        center = float(event["offset_s"])
        if not 6.0 <= center <= 398.0:
            continue
        for can_id, items in frames.items():
            before = in_window(items, center - 5.0, center - 1.0)
            after = in_window(items, center + 1.0, center + 5.0)
            if len(before) < 3 or len(after) < 3:
                continue
            before_rate = len(before) / 4.0
            after_rate = len(after) / 4.0
            if max(before_rate, after_rate) >= 0.5:
                ratio = (after_rate + 0.01) / (before_rate + 0.01)
                if ratio >= 2.0 or ratio <= 0.5:
                    rates.append(
                        {
                            **event,
                            "can_id": f"0x{can_id:03X}",
                            "before_hz": before_rate,
                            "after_hz": after_rate,
                            "ratio": ratio,
                        }
                    )
            dlc = min(min(map(len, before)), min(map(len, after)))
            pre = bit_prevalence(before, dlc)
            post = bit_prevalence(after, dlc)
            for index, (left, right) in enumerate(zip(pre, post)):
                delta = right - left
                # Strong, sustained bit transition. Rolling counters and checksums
                # normally remain mixed on both sides and do not pass this filter.
                if abs(delta) >= 0.80 and (left <= 0.10 or left >= 0.90) and (right <= 0.10 or right >= 0.90):
                    transitions.append(
                        {
                            **event,
                            "can_id": f"0x{can_id:03X}",
                            "byte": index // 8,
                            "bit_lsb0": index % 8,
                            "before_one_fraction": left,
                            "after_one_fraction": right,
                            "delta": delta,
                            "before_frames": len(before),
                            "after_frames": len(after),
                        }
                    )

    payload_snapshots = []
    focus_events = {"E03", "E04", "E06", "E08", "E09"}
    for event in events:
        if event["event_id"] not in focus_events:
            continue
        center = float(event["offset_s"])
        for can_id, items in frames.items():
            before = in_window(items, center - 5.0, center - 1.0)
            after = in_window(items, center + 1.0, center + 5.0)
            if not before or not after:
                continue
            pre_mode, pre_count = Counter(before).most_common(1)[0]
            post_mode, post_count = Counter(after).most_common(1)[0]
            if pre_mode != post_mode and pre_count / len(before) >= 0.5 and post_count / len(after) >= 0.5:
                payload_snapshots.append(
                    {
                        **event,
                        "can_id": f"0x{can_id:03X}",
                        "before_mode": pre_mode.hex(" "),
                        "after_mode": post_mode.hex(" "),
                        "before_mode_fraction": pre_count / len(before),
                        "after_mode_fraction": post_count / len(after),
                    }
                )

    result = {
        "asc_start_clock": start.isoformat(timespec="milliseconds"),
        "events": events,
        "frame_count": sum(len(items) for items in frames.values()),
        "can_id_count": len(frames),
        "inventory": inventory,
        "strong_bit_transitions": sorted(
            transitions,
            key=lambda item: (str(item["event_id"]), -abs(float(item["delta"])), str(item["can_id"])),
        ),
        "rate_changes": sorted(
            rates,
            key=lambda item: (str(item["event_id"]), -abs(float(item["ratio"]) - 1.0)),
        ),
        "stable_mode_changes": sorted(
            payload_snapshots,
            key=lambda item: (str(item["event_id"]), str(item["can_id"])),
        ),
    }
    (OUT / "raw_can_exploration.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "frames": result["frame_count"],
                "can_ids": result["can_id_count"],
                "strong_bit_transitions": len(transitions),
                "rate_changes": len(rates),
                "stable_mode_changes": len(payload_snapshots),
                "output": str(OUT / "raw_can_exploration.json"),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
