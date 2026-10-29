from pathlib import Path

import pytest

from paperbackwriter.outline import checkpoints, batches, sections, build_digest, planner_to_reader


def test_checkpoints_for_a_24_chapter_book_match_the_method():
    assert checkpoints(24) == (7, 12, 17, 21, 24)


def test_checkpoints_scale_with_length():
    assert checkpoints(20) == (6, 10, 14, 17, 20)


def test_batches_cover_every_chapter_once():
    ranges = batches(24)
    assert ranges == [(1, 7), (8, 12), (13, 17), (18, 21), (22, 24)]
    covered = [n for lo, hi in ranges for n in range(lo, hi + 1)]
    assert covered == list(range(1, 25))


def test_sections_splits_on_chapter_headings():
    text = "## Chapter 1: Fog\n\nA body.\n\n## Chapter 2: Tide\n\nA boat.\n"
    assert sections(text) == {1: ("Chapter 1: Fog", "A body."), 2: ("Chapter 2: Tide", "A boat.")}


def test_sections_refuses_a_duplicate_chapter():
    with pytest.raises(ValueError):
        sections("## Chapter 1: A\n\nx\n\n## Chapter 1: B\n\ny\n")


def _outline(tmp_path: Path, n: int) -> Path:
    half = n // 2
    first = "\n\n".join(f"## Chapter {i}: T{i}\n\nScene {i}.\nNotes: private {i}" for i in range(1, half + 1))
    second = "\n\n".join(f"## Chapter {i}: T{i}\n\nScene {i}." for i in range(half + 1, n + 1))
    (tmp_path / "04_chapters_a.md").write_text(first + "\n")
    (tmp_path / "05_chapters_b.md").write_text(second + "\n")
    return tmp_path


def test_digest_drops_notes_lines_and_writes_five_batches(tmp_path):
    root = _outline(tmp_path, 24)
    written = build_digest(root, 24)
    assert [p.name for p in written] == [f"batch{i}.md" for i in range(1, 6)]
    first = (root / "digest" / "batch1.md").read_text()
    assert "Chapter 7: T7" in first and "Chapter 8" not in first
    assert "private" not in first


def test_digest_refuses_a_missing_chapter(tmp_path):
    root = _outline(tmp_path, 24)
    (root / "05_chapters_b.md").write_text("## Chapter 13: T13\n\nScene.\n")
    with pytest.raises(ValueError):
        build_digest(root, 24)


def test_planner_to_reader_strips_clue_ids_and_labels(tmp_path):
    (tmp_path / "04_chapters_01_12.md").write_text(
        "**Ch 1. The Fog. Monday dawn. The quay.**\n"
        "- **Event:** The weigher finds the ledger (C3) torn.\n"
        "- [D]: She decides to keep it.\n"
        "- Not in this chapter: the steward.\n"
        "- The payoff comes later (4).\n"
    )
    out = planner_to_reader(tmp_path)
    text = out[0].read_text()
    assert text.startswith("## Chapter 1: The Fog\n\nMonday dawn. The quay.\n\n")
    assert "(C3)" not in text and "[D]" not in text and "Event:" not in text
    assert "steward" not in text
    assert "She decides to keep it." in text


def test_planner_to_reader_refuses_a_leftover_planner_mark(tmp_path):
    (tmp_path / "04_chapters_01_12.md").write_text("**Ch 1. A. B.**\n- see chapter 9 for this\n")
    with pytest.raises(ValueError):
        planner_to_reader(tmp_path)


def test_narration_heading_and_pronunciation_markup():
    from paperbackwriter.narrate import prepare, spoken_heading
    assert spoken_heading("Chapter 3: The Tide") == "Chapter Three. The Tide."
    assert prepare("“Murano,” she said.", {"Murano": "mʊɹˈɑːnoʊ"}) == '"[Murano](/mʊɹˈɑːnoʊ/)," she said.'
