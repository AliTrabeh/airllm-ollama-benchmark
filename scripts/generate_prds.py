"""Generate individual PRD markdown files from prd_catalog.json.

Usage:
    uv run python scripts/generate_prds.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = Path(__file__).resolve().parent / "prd_catalog.json"
OUT_DIR = ROOT / "docs" / "prds"

_TEMPLATE = """\
# {id}: {title}

**Group:** {group}
**Type:** {type}
**Target file:** `{file}`
**Status:** TODO

---

## Goal

{goal}

---

## Acceptance Criteria

{criteria}

---

## Dependencies

{deps}

---

## Notes

{notes}
"""


def _slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text[:55].strip("_")


def _fmt_checklist(items: list[str]) -> str:
    return "\n".join(f"- [ ] {item}" for item in items) if items else "- [ ] (none)"


def _fmt_deps(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "None"


def generate() -> None:
    if not CATALOG_PATH.exists():
        raise FileNotFoundError(f"Catalog not found: {CATALOG_PATH}")

    catalog: list[dict] = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))

    generated = 0
    for entry in catalog:
        group_dir = OUT_DIR / entry["group"]
        group_dir.mkdir(parents=True, exist_ok=True)

        prd_id = entry["id"].lower().replace("-", "_")
        slug = _slugify(entry["title"])
        fname = f"{prd_id}_{slug}.md"

        content = _TEMPLATE.format(
            id=entry["id"],
            title=entry["title"],
            group=entry["group"],
            type=entry.get("type", "implementation"),
            file=entry.get("file", "—"),
            goal=entry["goal"],
            criteria=_fmt_checklist(entry.get("criteria", [])),
            deps=_fmt_deps(entry.get("deps", [])),
            notes=entry.get("notes") or "—",
        )

        (group_dir / fname).write_text(content, encoding="utf-8")
        generated += 1

    print(f"Generated {generated} PRD files under {OUT_DIR}")
    print(f"Groups: {sorted({e['group'] for e in catalog})}")


if __name__ == "__main__":
    generate()
