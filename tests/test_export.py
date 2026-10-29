import re
import zipfile
from pathlib import Path

import pytest

from paperbackwriter.export import Book, load_chapters, build_epub, build_rtf, build_pdf
from paperbackwriter.proof import apply_fixes


def _chapters(tmp_path: Path) -> Path:
    d = tmp_path / "chapters"
    d.mkdir()
    (d / "ch01.txt").write_text("Chapter 1: The Long Tide\n\n“It was *cold*,” she said.\n\n* * *\n\nThe {ledger} & the key.\n")
    (d / "ch02.txt").write_text("Chapter 2: Tide\n\nThe boat came in at dawn.\n")
    return d


def test_load_chapters_reads_titles_and_bodies(tmp_path):
    chapters = load_chapters(_chapters(tmp_path))
    assert [c.title for c in chapters] == ["The Long Tide", "Tide"]
    assert chapters[1].text == "The boat came in at dawn."


def test_load_chapters_refuses_a_gap(tmp_path):
    d = _chapters(tmp_path)
    (d / "ch02.txt").rename(d / "ch03.txt")
    with pytest.raises(ValueError):
        load_chapters(d)


def _book(tmp_path):
    return Book(title="The Long Tide", author="A. Writer", chapters=load_chapters(_chapters(tmp_path)),
                series="The Test Mysteries, Book 1", note="Author’s Note\n\nThanks for reading.")


def test_epub_is_valid_shape_with_italics_and_escaping(tmp_path):
    out = build_epub(_book(tmp_path), tmp_path / "book.epub")
    with zipfile.ZipFile(out) as z:
        first = z.infolist()[0]
        assert first.filename == "mimetype" and first.compress_type == zipfile.ZIP_STORED
        ch1 = z.read("OEBPS/chapter_1.xhtml").decode()
        assert "<em>cold</em>" in ch1
        assert "&amp; the key" in ch1
        assert "* * *" in ch1  # a scene break is not an italic span
        opf = z.read("OEBPS/content.opf").decode()
        assert "A. Writer" in opf and "author-note.xhtml" in opf
        assert "Thanks for reading." in z.read("OEBPS/author-note.xhtml").decode()


def test_rtf_is_ascii_with_escapes_and_italics(tmp_path):
    out = build_rtf(_book(tmp_path), tmp_path / "book.rtf")
    text = out.read_text(encoding="ascii")
    assert r"{\i cold}" in text
    assert r"\{ledger\}" in text
    assert chr(92) + "u8220?" in text  # opening curly quote


def test_pdf_builds_with_one_page_per_chapter_at_least(tmp_path):
    out = build_pdf(_book(tmp_path), tmp_path / "book.pdf")
    data = out.read_bytes()
    assert data.startswith(b"%PDF")
    pages = max(int(n) for n in re.findall(rb"/Count (\d+)", data))
    assert pages >= 4  # title page, two chapters, author's note


def test_apply_fixes_replaces_unique_strings_and_skips_ambiguous_ones(tmp_path):
    d = _chapters(tmp_path)
    applied, skipped = apply_fixes(d, [
        {"file": "ch02.txt", "old": "at dawn", "new": "at noon"},
        {"file": "ch01.txt", "old": "e", "new": "a"},
    ])
    assert (applied, len(skipped)) == (1, 1)
    assert "at noon" in (d / "ch02.txt").read_text()


def test_apply_fixes_dry_run_changes_nothing(tmp_path):
    d = _chapters(tmp_path)
    apply_fixes(d, [{"file": "ch02.txt", "old": "at dawn", "new": "at noon"}], dry=True)
    assert "at dawn" in (d / "ch02.txt").read_text()
