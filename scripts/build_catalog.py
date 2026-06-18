"""Build prd_catalog.json from all group data files.

Usage:
    python scripts/build_catalog.py
"""
from __future__ import annotations

import json
from pathlib import Path

from catalog import g00, g01, g02, g03, g04, g05
from catalog import g06, g07, g08, g09, g10, g11, g12, g13

OUT = Path(__file__).parent / "prd_catalog.json"

GROUPS = [g00, g01, g02, g03, g04, g05, g06, g07, g08, g09, g10, g11, g12, g13]


def build() -> list[dict]:
    catalog: list[dict] = []
    for mod in GROUPS:
        group_name: str = mod.G
        prefix = group_name.split("_")[0].upper()
        for idx, entry in enumerate(mod.PRDS, start=1):
            title, type_, file_, goal = entry
            catalog.append({
                "id": f"PRD-{prefix}-{idx:03d}",
                "group": group_name,
                "title": title,
                "type": type_,
                "file": file_,
                "goal": goal,
                "criteria": [],
                "deps": [],
                "notes": "",
            })
    return catalog


if __name__ == "__main__":
    catalog = build()
    OUT.write_text(json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8")
    by_group = {}
    for e in catalog:
        by_group.setdefault(e["group"], 0)
        by_group[e["group"]] += 1
    print(f"Total PRDs: {len(catalog)}")
    for g, c in sorted(by_group.items()):
        print(f"  {g}: {c}")
