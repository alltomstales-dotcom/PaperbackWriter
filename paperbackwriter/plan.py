"""Check a book plan's structure without printing spoilers.

A plan folder holds the plan files (see the method docs), the chapter outlines
(converted to reader form in reader/ when written in planner form), a digest/ folder
built from the reader outlines, and the writer brief here or one level up. This checks
structure only: file presence, the 2,000-word cap, chapter coverage, and that every
digest batch matches the stripped outline exactly. It does not judge the mystery;
that is the plan read's job.
"""
from __future__ import annotations

import re
from pathlib import Path

from .outline import batches, sections

FIXED = ("01_solution_and_suspects.md", "02a_curve.md", "02b_clues.md",
         "03_resolution_map.md", "canon.md", "audit.md")
WORD_CAP = 2000


def check_plan(root: Path, n_chapters: int = 24) -> dict:
    root = Path(root)
    errors: list[str] = []
    counts: dict[str, int] = {}
    planner = sorted(root.glob("0*_chapters_*.md"))
    # Planner-format outlines are converted by `paperbackwriter reader` into root/reader/;
    # the digest is then built there. Outlines already in reader format sit in root itself.
    reader_dir = root / "reader" if (root / "reader").is_dir() else root
    outline = sorted(reader_dir.glob("0*_chapters_*.md"))
    for name in FIXED:
        if not (root / name).is_file():
            errors.append(f"Missing {name}")
    if not outline:
        errors.append("Missing chapter outline files (0N_chapters_*.md)")
    for path in [root / name for name in FIXED] + planner:
        if path.is_file():
            counts[path.name] = len(path.read_text(encoding="utf-8").split())
            if not 0 < counts[path.name] < WORD_CAP:
                errors.append(f"{path.name} must contain fewer than 2,000 words")

    source: dict[int, tuple[str, str]] = {}
    for path in outline:
        try:
            parsed = sections(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            errors.append(f"{path.name}: {exc}")
            continue
        for n, (title, body) in parsed.items():
            if n in source:
                errors.append(f"Chapter {n} appears in more than one outline file")
            # Planner notes start at "Notes:"; none reach a reader.
            source[n] = (title, re.split(r"(?m)^Notes:", body, maxsplit=1)[0].strip())
    if outline and set(source) != set(range(1, n_chapters + 1)):
        errors.append(f"Outline files do not cover chapters 1-{n_chapters} exactly once")

    ranges = batches(n_chapters)
    digest = sorted((reader_dir / "digest").glob("batch*.md"))
    if len(digest) != len(ranges):
        errors.append(f"Exactly {len(ranges)} digest batches required")
    for path, (lo, hi) in zip(digest, ranges):
        try:
            parsed = sections(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            errors.append(f"{path.name}: {exc}")
            continue
        if set(parsed) != set(range(lo, hi + 1)):
            errors.append(f"Wrong chapter coverage in {path.name}")
        for n, value in parsed.items():
            if value != source.get(n):
                errors.append(f"Digest chapter {n} differs from stripped outline")

    if not any(p.is_file() for p in (root / "WRITER_BRIEF.md", root.parent / "WRITER_BRIEF.md")):
        errors.append("Missing writer brief")
    return {"plan": str(root), "word_counts": counts, "digest_batches": len(digest),
            "chapters": len(source), "passed": not errors, "errors": errors}
