"""Command line: `paperbackwriter <command>` (or `python -m paperbackwriter <command>`)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _print(result) -> int:
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not isinstance(result, dict) or result.get("passed", True) else 1


def cmd_reader(a):
    from .outline import planner_to_reader
    for p in planner_to_reader(Path(a.plan), tuple(a.drop or ())):
        print(p)
    return 0


def cmd_digest(a):
    from .outline import build_digest
    for p in build_digest(Path(a.outline), a.chapters):
        print(f"{p}: {len(p.read_text(encoding='utf-8').split())} words")
    return 0


def cmd_check_plan(a):
    from .plan import check_plan
    return _print(check_plan(Path(a.plan), a.chapters))


def cmd_stage(a):
    from .reads import stage
    print(f"released {stage(Path(a.chapters_dir), Path(a.read_dir), a.upto)} chapters through {a.upto}")
    return 0


def cmd_check_read(a):
    from .reads import check_log, ranking
    result = check_log(Path(a.log), a.finished)
    if a.answer:
        result["rank"], result["probability"] = ranking(Path(a.log), a.answer)
    return _print(result)


def cmd_gate(a):
    from .reads import advance_plan_read
    return _print(advance_plan_read(Path(a.reference), Path(a.gate), a.checkpoint, a.chapters))


def cmd_proof(a):
    from .proof import apply_fixes
    fixes_path = Path(a.fixes)
    chapters = Path(a.chapters_dir) if a.chapters_dir else fixes_path.parent / "chapters"
    applied, skipped = apply_fixes(chapters, json.loads(fixes_path.read_text(encoding="utf-8")), a.dry)
    for line in skipped:
        print(line)
    print(f"applied {applied}, skipped {len(skipped)}" + (" (dry run)" if a.dry else ""))
    return 0 if not skipped else 1


def cmd_export(a):
    from .export import Book, build_epub, build_pdf, build_rtf, load_chapters
    note = Path(a.note).read_text(encoding="utf-8") if a.note else ""
    book = Book(title=a.title, author=a.author, chapters=load_chapters(Path(a.chapters_dir)),
                series=a.series or "", note=note)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    slug = a.slug or "-".join(a.title.lower().split())
    built = [build_epub(book, out / f"{slug}.epub"), build_rtf(book, out / f"{slug}.rtf")]
    if not a.no_pdf:
        built.append(build_pdf(book, out / f"{slug}.pdf", regular=a.font, italic=a.italic_font))
    words = sum(len(c.text.split()) for c in book.chapters)
    print(f"{book.title}: {len(book.chapters)} chapters, {words:,} words")
    for p in built:
        print(f"  {p} ({p.stat().st_size:,} bytes)")
    return 0


def cmd_narrate(a):
    from .narrate import narrate
    minutes = narrate(Path(a.chapter), Path(a.out), a.voice, a.speed, a.lang, a.pronunciations, a.max_paragraphs)
    print(f"{a.out}: {minutes:.1f} min")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="paperbackwriter", description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("reader", help="planner chapter files -> reader outlines (plan/reader/)")
    s.add_argument("plan")
    s.add_argument("--drop", action="append", help="regex for another planner-only line to drop")
    s.set_defaults(func=cmd_reader)

    s = sub.add_parser("digest", help="reader outlines -> digest/batchN.md for a staged plan read")
    s.add_argument("outline")
    s.add_argument("--chapters", type=int, default=24)
    s.set_defaults(func=cmd_digest)

    s = sub.add_parser("check-plan", help="structural check of a plan folder (no spoilers printed)")
    s.add_argument("plan")
    s.add_argument("--chapters", type=int, default=24)
    s.set_defaults(func=cmd_check_plan)

    s = sub.add_parser("stage", help="release chapters 1..N into a blind reader's folder")
    s.add_argument("chapters_dir")
    s.add_argument("read_dir")
    s.add_argument("upto", type=int)
    s.set_defaults(func=cmd_stage)

    s = sub.add_parser("check-read", help="verify a reader's checkpoint log (quotes, probabilities)")
    s.add_argument("log")
    s.add_argument("--answer", help="intended culprit's name, to print their rank")
    s.add_argument("--finished", action="store_true", help="audit a completed read (later chapters on disk)")
    s.set_defaults(func=cmd_check_read)

    s = sub.add_parser("gate", help="score a plan-read checkpoint and release the next batch if it passes")
    s.add_argument("reference")
    s.add_argument("gate")
    s.add_argument("checkpoint", type=int)
    s.add_argument("--chapters", type=int, default=24)
    s.set_defaults(func=cmd_gate)

    s = sub.add_parser("proof", help="apply exact-string fixes from a JSON list")
    s.add_argument("fixes")
    s.add_argument("--chapters-dir")
    s.add_argument("--dry", action="store_true")
    s.set_defaults(func=cmd_proof)

    s = sub.add_parser("export", help="build EPUB, RTF and PDF from chNN.txt files")
    s.add_argument("chapters_dir")
    s.add_argument("--title", required=True)
    s.add_argument("--author", required=True)
    s.add_argument("--series")
    s.add_argument("--note", help="author's note text file, placed after the last chapter")
    s.add_argument("--out", default="release")
    s.add_argument("--slug")
    s.add_argument("--font", help="regular .ttf for the PDF")
    s.add_argument("--italic-font", help="italic .ttf for the PDF")
    s.add_argument("--no-pdf", action="store_true")
    s.set_defaults(func=cmd_export)

    s = sub.add_parser("narrate", help="chapter -> WAV with Kokoro TTS")
    s.add_argument("chapter")
    s.add_argument("out")
    s.add_argument("--voice", default="bm_george")
    s.add_argument("--speed", type=float, default=0.95)
    s.add_argument("--lang", default="b", help="Kokoro language code: a = American, b = British")
    s.add_argument("--pronunciations", help='JSON {"word": "IPA"} overrides')
    s.add_argument("--max-paragraphs", type=int, default=0)
    s.set_defaults(func=cmd_narrate)

    a = p.parse_args(argv)
    try:
        return a.func(a)
    except (ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
