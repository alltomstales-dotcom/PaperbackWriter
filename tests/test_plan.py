from pathlib import Path

from paperbackwriter.outline import build_digest
from paperbackwriter.plan import check_plan

FIXED = ("01_solution_and_suspects.md", "02a_curve.md", "02b_clues.md", "03_resolution_map.md",
         "canon.md", "audit.md")


def _plan(root: Path) -> Path:
    for name in FIXED:
        (root / name).write_text("words " * 50)
    (root / "04_chapters_01_12.md").write_text(
        "\n\n".join(f"## Chapter {i}: T{i}\n\nScene {i}.\nNotes: private" for i in range(1, 13)) + "\n")
    (root / "05_chapters_13_24.md").write_text(
        "\n\n".join(f"## Chapter {i}: T{i}\n\nScene {i}." for i in range(13, 25)) + "\n")
    (root / "WRITER_BRIEF.md").write_text("brief\n")
    build_digest(root, 24)
    return root


def test_a_complete_plan_passes(tmp_path):
    result = check_plan(_plan(tmp_path))
    assert result["passed"], result["errors"]


def test_an_overlong_plan_file_fails(tmp_path):
    root = _plan(tmp_path)
    (root / "canon.md").write_text("word " * 2001)
    assert "canon.md must contain fewer than 2,000 words" in check_plan(root)["errors"]


def test_a_digest_that_drifted_from_the_outline_fails(tmp_path):
    root = _plan(tmp_path)
    (root / "04_chapters_01_12.md").write_text(
        (root / "04_chapters_01_12.md").read_text().replace("Scene 3.", "Scene three, rewritten."))
    assert "Digest chapter 3 differs from stripped outline" in check_plan(root)["errors"]


def test_a_missing_file_is_named(tmp_path):
    root = _plan(tmp_path)
    (root / "02b_clues.md").unlink()
    assert "Missing 02b_clues.md" in check_plan(root)["errors"]


def test_outline_may_be_split_into_more_than_two_files(tmp_path):
    root = _plan(tmp_path)
    text = (root / "05_chapters_13_24.md").read_text()
    first, second = text.split("## Chapter 19:")
    (root / "05_chapters_13_24.md").unlink()
    (root / "05_chapters_13_18.md").write_text(first)
    (root / "06_chapters_19_24.md").write_text("## Chapter 19:" + second)
    result = check_plan(root)
    assert result["passed"], result["errors"]


def test_a_chapter_in_two_outline_files_fails(tmp_path):
    root = _plan(tmp_path)
    (root / "06_chapters_extra.md").write_text("## Chapter 5: Again\n\nScene.\n")
    assert "Chapter 5 appears in more than one outline file" in check_plan(root)["errors"]


def test_planner_outlines_are_checked_through_their_reader_folder(tmp_path):
    from paperbackwriter.outline import planner_to_reader
    for name in FIXED:
        (tmp_path / name).write_text("words " * 50)
    (tmp_path / "WRITER_BRIEF.md").write_text("brief\n")
    (tmp_path / "04_chapters_01_24.md").write_text("\n".join(
        f"**Ch {i}. Title {i}. Day {i}. The quay.**\n- **Event:** Thing {i} happens.\n" for i in range(1, 25)))
    planner_to_reader(tmp_path)
    build_digest(tmp_path / "reader", 24)
    result = check_plan(tmp_path)
    assert result["passed"], result["errors"]
