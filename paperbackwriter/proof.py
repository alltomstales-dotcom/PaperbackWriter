"""Apply proofread and fix-pass corrections as exact-string replacements.

Fixes JSON: [{"file": "ch05.txt", "old": "...", "new": "..."}, ...]
Each old string must occur exactly once in its file, or that fix is skipped and reported,
so a correction can never land in the wrong sentence.
"""
from __future__ import annotations

from pathlib import Path


def apply_fixes(chapters_dir: Path, fixes: list[dict], dry: bool = False) -> tuple[int, list[str]]:
    """Return (applied count, skip messages)."""
    chapters_dir = Path(chapters_dir)
    applied, skipped = 0, []
    for fix in fixes:
        path = chapters_dir / fix["file"]
        text = path.read_text(encoding="utf-8")
        count = text.count(fix["old"])
        if count != 1:
            skipped.append(f"SKIP {fix['file']}: old found {count} times: {fix['old'][:60]!r}")
            continue
        if not dry:
            path.write_text(text.replace(fix["old"], fix["new"]), encoding="utf-8")
        applied += 1
    return applied, skipped
