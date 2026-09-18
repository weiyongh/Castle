"""Relate S0035 raw CAN candidates without assigning Signal semantics.

Artifact Metadata
author: Analyst
version: 0.1
create_time: 2026-09-17
update_time: 2026-09-17
status: DRAFT

Consumes the hypothesis-conditioned phase candidates and collapses bit-level
duplicates into temporal transition-pair clusters. The output describes
co-movement and ordering, not causality or Signal identity.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


SOURCE = Path(
    "/Users/hwy/Castle/people/acqanalyst/work/analysis_s0035/raw_can/"
    "phase_bit_candidates.json"
)
OUTPUT = SOURCE.with_name("candidate_relations.json")


def clean_pairs(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pairs = []
    for record in records:
        changes = record["transitions"]
        if len(changes) != 2:
            continue
        first, second = changes
        if first["from"] != second["to"] or first["to"] != second["from"]:
            continue
        pairs.append(
            {
                "can_id": record["can_id"],
                "byte": record["byte"],
                "bit_lsb0": record["bit_lsb0"],
                "start_s": first["time_s"],
                "end_s": second["time_s"],
                "active_value": first["to"],
            }
        )
    return pairs


def cluster_pairs(pairs: list[dict[str, Any]], tolerance_s: float = 0.25) -> list[dict[str, Any]]:
    clusters: list[list[dict[str, Any]]] = []
    for pair in sorted(pairs, key=lambda item: (item["start_s"], item["end_s"])):
        for cluster in clusters:
            start_mean = sum(item["start_s"] for item in cluster) / len(cluster)
            end_mean = sum(item["end_s"] for item in cluster) / len(cluster)
            if abs(pair["start_s"] - start_mean) <= tolerance_s and abs(pair["end_s"] - end_mean) <= tolerance_s:
                cluster.append(pair)
                break
        else:
            clusters.append([pair])
    result = []
    for index, cluster in enumerate(sorted(clusters, key=lambda group: min(item["start_s"] for item in group)), 1):
        by_id: dict[str, int] = defaultdict(int)
        for item in cluster:
            by_id[item["can_id"]] += 1
        result.append(
            {
                "cluster_id": index,
                "bit_count": len(cluster),
                "can_id_count": len(by_id),
                "can_ids": dict(sorted(by_id.items())),
                "start_min_s": min(item["start_s"] for item in cluster),
                "start_max_s": max(item["start_s"] for item in cluster),
                "start_mean_s": sum(item["start_s"] for item in cluster) / len(cluster),
                "end_min_s": min(item["end_s"] for item in cluster),
                "end_max_s": max(item["end_s"] for item in cluster),
                "end_mean_s": sum(item["end_s"] for item in cluster) / len(cluster),
                "members": cluster,
            }
        )
    return result


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    charge_pairs = clean_pairs(source["charge_plateau_candidates"])
    plug_pairs = clean_pairs(source["plug_plateau_candidates"])
    result = {
        "method": {
            "input_warning": "Input candidates were selected with predefined phase windows.",
            "pair_rule": "Exactly two opposite-direction transitions in the ASC.",
            "cluster_tolerance_s": 0.25,
            "meaning": "Temporal co-movement only; no causality or Signal semantics.",
        },
        "charge_pairs": charge_pairs,
        "charge_pair_clusters": cluster_pairs(charge_pairs),
        "plug_pairs": plug_pairs,
        "plug_pair_clusters": cluster_pairs(plug_pairs),
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "charge_pairs": len(charge_pairs),
        "charge_clusters": len(result["charge_pair_clusters"]),
        "plug_pairs": len(plug_pairs),
        "plug_clusters": len(result["plug_pair_clusters"]),
        "output": str(OUTPUT),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
