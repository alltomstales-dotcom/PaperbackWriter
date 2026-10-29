"""Chapter outlines: checkpoints, reader outlines and the staged digest for a plan read.

A plan read gives a fresh reader the book as a plain outline, one batch at a time,
before any prose exists. These helpers turn the planner's chapter files (which carry
clue IDs, decision marks and notes) into what a reader would actually see.
"""
from __future__ import annotations

import re
from pathlib import Path

HEADING = re.compile(r"(?m)^(?:#{1,4}\s+)?Chapter\s+(\d+)\b[^\n]*\n")
CHAPTER_BLOCK = re.compile(r"(?ms)^## Chapter (\d+): ([^\n]*)\n(.*?)(?=^#{1,2} |\Z)")

# Planner lines that never reach a reader.
PLANNER_ONLY = (r"^[Nn]ot in this chapter", r"^\S+:? not in this chapter", r"^No confession does evidentiary work")
# Clue IDs like (C3), (M2 at 14), chapter cross-references like (4) or (7, 12), file refs like (02b).
REF = re.compile(r"\s*\((?:[CMTH]\d+[^)]*|\d+(?:[,–-]\s*\d+)*(?:, confirmed at \d+)?|0\d[^)]*)\)")
LEFTOVER = re.compile(r"\([CMTH]\d|\[D|\b(?:ch|chapter) \d|(?<![.\d])\b0\d\b")


def checkpoints(n_chapters: int) -> tuple[int, ...]:
    """Reader checkpoints: about 30%, 50% and 70%, the chapter before the reveal, and the end."""
    n = n_chapters
    return (round(n * 0.3), round(n * 0.5), round(n * 0.7), n - 3, n)


def batches(n_chapters: int) -> list[tuple[int, int]]:
    """Inclusive chapter ranges released to the reader, one per checkpoint."""
    out, lo = [], 1
    for hi in checkpoints(n_chapters):
        out.append((lo, hi))
        lo = hi + 1
    return out


def sections(text: str) -> dict[int, tuple[str, str]]:
    """Split text on "Chapter N" headings: {N: (heading, body)}."""
    matches = list(HEADING.finditer(text))
    result: dict[int, tuple[str, str]] = {}
    for i, match in enumerate(matches):
        number = int(match.group(1))
        if number in result:
            raise ValueError(f"Duplicate chapter {number}")
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        result[number] = (match.group().strip().lstrip("# "), text[match.end():end].strip())
    return result


def build_digest(root: Path, n_chapters: int = 24) -> list[Path]:
    """Write root/digest/batchN.md from every 0*_chapters_*.md in root. "Notes:" lines are dropped."""
    root = Path(root)
    text = "\n".join(p.read_text(encoding="utf-8") for p in sorted(root.glob("0*_chapters_*.md")))
    chap = {}
    for m in CHAPTER_BLOCK.finditer(text):
        body = "\n".join(l for l in m.group(3).strip().splitlines() if not l.startswith("Notes:")).strip()
        chap[int(m.group(1))] = (m.group(2).strip(), body)
    if sorted(chap) != list(range(1, n_chapters + 1)):
        missing = sorted(set(range(1, n_chapters + 1)) - set(chap))
        raise ValueError(f"outline does not cover chapters 1-{n_chapters}; missing {missing}")
    out = root / "digest"
    out.mkdir(exist_ok=True)
    written = []
    for i, (lo, hi) in enumerate(batches(n_chapters), 1):
        t = "\n\n".join(f"Chapter {n}: {chap[n][0]}\n\n{chap[n][1]}" for n in range(lo, hi + 1)) + "\n"
        path = out / f"batch{i}.md"
        path.write_text(t, encoding="utf-8")
        written.append(path)
    return written


def _clean(text: str) -> str:
    text = re.sub(r"\[D(?::[^\]]*)?\]:?\s*", "", text)
    text = REF.sub("", text)
    text = text.replace("**", "").replace("*", "")
    left = LEFTOVER.findall(text)
    if left:
        raise ValueError(f"planner marks left in reader text {left}: {text[:120]!r}")
    return re.sub(r"\s+", " ", text).strip()


def _planner_chapters(md: str, drop: tuple[str, ...]):
    for block in re.split(r"(?m)^(?=\*\*Ch \d+\. )", md):
        m = re.match(r"\*\*Ch (\d+)\. ([^.]+)\. (.*?)\*\*\s*\n(.*)", block, re.S)
        if not m:
            continue
        n, title, head, body = m.groups()
        sentences = []
        for line in body.splitlines():
            s = line.strip()
            if not s:
                continue
            s = re.sub(r"^(?:[-*]|\d+\.)\s+", "", s)                    # bullet or number
            label = re.match(r"^\*\*([^*]{1,60}?):\*\*\s*", s)           # "**Label:**"
            if label:
                s = s[label.end():]
                if s.startswith('"'):                                   # a bare quote keeps its speaker
                    s = f"{label.group(1)}: {s}"
            s = re.sub(r"^\[D\]:\s*", "", s)
            if not s or any(re.match(p, s.replace("**", "")) for p in drop):
                continue
            s = s[0].upper() + s[1:]
            if s.endswith(":"):                                         # a list lead-in keeps its colon
                sentences.append(s)
                continue
            if s.endswith('"') and len(s) > 1 and s[-2] not in ".!?,":
                s += "."
            sentences.append(s if s[-1] in ".!?\"'”)" else s + ".")
        yield int(n), title.strip(), _clean(head), _clean(" ".join(sentences))


def planner_to_reader(root: Path, extra_drop: tuple[str, ...] = ()) -> list[Path]:
    """Turn planner chapter files into reader outlines in root/reader/.

    Planner format: a "**Ch N. Title. When. Where.**" line, then bullets
    ("- **Label:** text", nested bullets, numbered items). Labels, clue IDs, [D] decision
    marks, chapter cross-references and planner-only lines are removed. extra_drop adds
    regexes for more planner-only lines (for example a character who is "not in this chapter").
    """
    root = Path(root)
    out = root / "reader"
    out.mkdir(exist_ok=True)
    written = []
    for p in sorted(root.glob("0*_chapters_*.md")):
        parts = [f"## Chapter {n}: {t}\n\n{h}\n\n{b}"
                 for n, t, h, b in _planner_chapters(p.read_text(encoding="utf-8"), PLANNER_ONLY + tuple(extra_drop))]
        if not parts:
            raise ValueError(f"{p.name}: no '**Ch N. Title. When. Where.**' chapters found")
        target = out / p.name
        target.write_text("\n\n".join(parts) + "\n", encoding="utf-8")
        written.append(target)
    return written
