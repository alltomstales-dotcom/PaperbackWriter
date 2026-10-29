"""Blind reads: stage chapters for a fresh reader, verify their logs, and gate a plan read.

A reader writes log_chNN.json at each checkpoint: every suspect with a probability and
exact quotes. Every quote is checked by string search against the text the reader was
actually given; an invented quote voids the log. Nothing here prints plot details
beyond the names the reader wrote.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

from .outline import checkpoints, sections

CHAPTER_FILE = re.compile(r"ch(\d+)\.txt")
BATCH_HEADING = re.compile(r"(?m)^(?:(?:#{1,4}\s+)?(?:Chapter|Ch\.?|chapter)\s+(\d+)\b|\*\*(\d+)\.)[^\n]*")


def _staged_text(folder: Path) -> dict[int, str]:
    chapters: dict[int, str] = {}
    for source in sorted(folder.glob("ch*.txt")):
        m = CHAPTER_FILE.fullmatch(source.name)
        if m:
            chapters[int(m.group(1))] = source.read_text(encoding="utf-8")
    for source in sorted(folder.glob("batch*.md")):
        text = source.read_text(encoding="utf-8")
        headings = list(BATCH_HEADING.finditer(text))
        for i, heading in enumerate(headings):
            number = int(heading.group(1) or heading.group(2))
            end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
            chapters[number] = text[heading.start():end]
    return chapters


def _quotes(value):
    """Every {"chapter": n, "quote": "..."} item anywhere in a log or verdict."""
    if isinstance(value, dict):
        if "quote" in value:
            yield value
        for item in value.values():
            yield from _quotes(item)
    elif isinstance(value, list):
        for item in value:
            yield from _quotes(item)


def check_log(path: Path, finished: bool = False) -> dict:
    """Verify a checkpoint log against the text staged next to it.

    During a read, the folder must hold exactly chapters 1 through the checkpoint.
    finished=True audits a completed read, where later chapters have since been released:
    only the quotes are checked, against chapters 1 through the checkpoint.
    """
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    checkpoint = int(data["after_chapter"])
    chapters = _staged_text(path.parent)
    if finished:
        chapters = {n: t for n, t in chapters.items() if n <= checkpoint}
    errors = []
    if not chapters:
        errors.append("No recognizable chapter text in staged folder")
    if set(chapters) != set(range(1, checkpoint + 1)):
        errors.append("Staged chapters must be exactly chapters 1 through the checkpoint")
    probabilities = [entry["p_culprit"] for entry in data["suspects"]]
    if not all(isinstance(p, (int, float)) and 0 <= p <= 1 for p in probabilities):
        errors.append("Invalid probability")
    if abs(sum(probabilities) - 1) > 1e-6:
        errors.append("Probabilities do not sum to one")
    evidence = list(_quotes(data))
    for i, item in enumerate(evidence, 1):
        quote, number = item.get("quote", ""), item.get("chapter")
        if not quote or quote not in chapters.get(number, ""):
            errors.append(f"Evidence {i}: quotation absent from cited chapter")
    return {"log": str(path), "checkpoint": checkpoint, "evidence_count": len(evidence),
            "passed": not errors, "errors": errors}


def _entry(suspects: list[dict], answer: str):
    """The one suspect entry naming the intended answer: full name, then surname, then first name."""
    for key in (answer, answer.split()[-1], answer.split()[0]):
        hits = [s for s in suspects if re.search(r"\b" + re.escape(key) + r"\b", s["name"], re.I)]
        if len(hits) == 1:
            return hits[0]
        if len(hits) > 1 and key != answer:
            raise ValueError(f"'{key}' matches more than one suspect; use a fuller name")
    return None


def ranking(log_path: Path, answer: str) -> tuple[int, float]:
    """(rank, probability) the reader gave the intended answer. Not listed = probability 0."""
    suspects = json.loads(Path(log_path).read_text(encoding="utf-8"))["suspects"]
    entry = _entry(suspects, answer)
    p = entry["p_culprit"] if entry else 0.0
    return 1 + sum(s["p_culprit"] > p for s in suspects), p


def stage(chapters_dir: Path, read_dir: Path, upto: int) -> int:
    """Copy chapters up to `upto` into a reader's folder. Later chapters never exist there early."""
    chapters_dir, read_dir = Path(chapters_dir), Path(read_dir)
    read_dir.mkdir(parents=True, exist_ok=True)
    have = [int(CHAPTER_FILE.fullmatch(p.name).group(1)) for p in read_dir.glob("ch*.txt")
            if CHAPTER_FILE.fullmatch(p.name)]
    start = max(have, default=0) + 1
    if upto < start:
        raise ValueError(f"reader already has chapters through {start - 1}")
    copied = 0
    for n in range(start, upto + 1):
        source = chapters_dir / f"ch{n:02d}.txt"
        if not source.is_file():
            raise ValueError(f"missing {source}")
        shutil.copy2(source, read_dir / source.name)
        copied += 1
    return copied


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def advance_plan_read(reference: Path, gate_path: Path, checkpoint: int, n_chapters: int = 24) -> dict:
    """Score one plan-read checkpoint and, if it passes, release the next digest batch.

    reference (written privately BEFORE the read, so the answer cannot drift):
      {"candidate_directory": plan dir holding digest/, "reader_folder": the reader's folder,
       "plan_sha256": {file: hash}, "digest_sha256": {batchN.md: hash}, "intended_answer": "Full Name"}
    gate: {"checkpoints": []}, appended to at each call, in order.

    Pass rule: the intended answer is outside the reader's top two at the first two
    checkpoints, and at or under .35 at the third.
    """
    reference, gate_path = Path(reference), Path(gate_path)
    points = checkpoints(n_chapters)
    if checkpoint not in points:
        raise ValueError(f"checkpoint must be one of {points}")
    ref = json.loads(reference.read_text(encoding="utf-8"))
    base = reference.parent
    candidate = (base / ref["candidate_directory"]).resolve()
    folder = (base / ref["reader_folder"]).resolve()
    for name, h in ref["plan_sha256"].items():
        if _sha(candidate / name) != h:
            raise ValueError(f"plan file changed since the reference was written: {name}")
    for name, h in ref["digest_sha256"].items():
        if _sha(candidate / "digest" / name) != h:
            raise ValueError(f"digest changed since the reference was written: {name}")
        if (folder / name).exists() and _sha(folder / name) != h:
            raise ValueError(f"reader batch changed: {name}")
    log_path = folder / f"log_ch{checkpoint:02d}.json"
    result = check_log(log_path)
    if not result["passed"]:
        raise ValueError(f"log failed verification: {result['errors']}")
    rank, p = ranking(log_path, ref["intended_answer"])
    index = points.index(checkpoint)
    passed = rank > 2 if index < 2 else p <= 0.35 if index == 2 else True
    record = dict(checkpoint=checkpoint, rank=rank, probability=p,
                  exact_quotes=result["evidence_count"], passed=passed)
    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    if len(gate["checkpoints"]) != index:
        raise ValueError("checkpoints must be scored in order")
    if checkpoint == points[-1] and (folder / "verdict.json").exists():
        verdict = json.loads((folder / "verdict.json").read_text(encoding="utf-8"))
        source = {n: body for path in sorted(folder.glob("batch*.md"))
                  for n, (_, body) in sections(path.read_text(encoding="utf-8")).items()}
        bad = [q for q in _quotes(verdict) if q.get("quote") not in source.get(int(q.get("chapter", 0)), "")]
        record.update(verdict_quotes_invalid=len(bad),
                      scores={k: verdict[k] for k in ("overall", "fair_play", "misdirection", "solution")
                              if k in verdict},
                      obvious_chapter=verdict.get("when_culprit_became_obvious"))
    gate["checkpoints"].append(record)
    gate["gate_passed"] = len(gate["checkpoints"]) >= 3 and all(r["passed"] for r in gate["checkpoints"][:3])
    if not passed:
        gate["stage"] = f"FAILED_AT_{checkpoint}"
    elif checkpoint < points[-1]:
        name = f"batch{index + 2}.md"
        if (folder / name).exists():
            raise ValueError("next batch was already released")
        shutil.copy2(candidate / "digest" / name, folder / name)
        record["released_through"] = points[index + 1]
        gate["stage"] = "EARLY_GATE_PASSED" if gate["gate_passed"] else "RUNNING"
    else:
        gate["stage"] = "READ_COMPLETE"
    gate_path.write_text(json.dumps(gate, indent=2) + "\n", encoding="utf-8")
    return record
