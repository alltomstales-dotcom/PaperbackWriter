"""Build a reading edition of a book: EPUB 3, RTF and a 6x9 PDF.

Chapters are plain-text files chNN.txt: first line "Chapter N: Title", a blank line,
then paragraphs separated by blank lines. *Asterisks* mark italics. A line of
"* * *" is a scene break and is never read as italics.

EPUB and RTF need only the standard library. PDF needs fpdf2 and a Unicode TTF font
(DejaVu Serif is found automatically on most Linux systems; pass font paths otherwise).
"""
from __future__ import annotations

import html
import re
import uuid
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

CHAPTER_FILE = re.compile(r"ch(\d+)\.txt")
HEAD = re.compile(r"Chapter (\d+): (.+)")
# Italic spans start and end on a non-space, so a "* * *" scene break is left alone.
ITALIC = re.compile(r"\*(\S(?:[^*\n]*\S)?)\*")
SCENE_BREAK = "* * *"

FONT_DIRS = ("/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/dejavu", "/Library/Fonts",
             str(Path.home() / "Library/Fonts"), "C:/Windows/Fonts")


@dataclass
class Chapter:
    index: int
    title: str
    text: str

    @property
    def paragraphs(self) -> list[str]:
        return [p.strip() for p in self.text.split("\n\n") if p.strip()]


@dataclass
class Book:
    title: str
    author: str
    chapters: list[Chapter]
    series: str = ""          # e.g. "The Harbour Mysteries, Book 1"
    note: str = ""            # an author's note, placed after the last chapter
    language: str = "en"
    identifier: str = field(default_factory=lambda: f"urn:uuid:{uuid.uuid4()}")


def load_chapters(chapters_dir: Path) -> list[Chapter]:
    chapters = []
    for path in sorted(Path(chapters_dir).glob("ch*.txt")):
        if not CHAPTER_FILE.fullmatch(path.name):
            continue
        raw = path.read_text(encoding="utf-8").strip()
        head, _, body = raw.partition("\n")
        match = HEAD.fullmatch(head.strip())
        if not match:
            raise ValueError(f"{path.name}: first line is not 'Chapter N: Title'")
        number = int(match.group(1))
        if number != int(CHAPTER_FILE.fullmatch(path.name).group(1)):
            raise ValueError(f"{path.name}: heading says Chapter {number}")
        chapters.append(Chapter(number, match.group(2).strip(), body.strip()))
    if not chapters:
        raise ValueError(f"no chNN.txt files in {chapters_dir}")
    if [c.index for c in chapters] != list(range(1, len(chapters) + 1)):
        raise ValueError("chapter numbers are not 1..N in order")
    return chapters


def _note_paragraphs(note: str) -> list[str]:
    paras = [p.strip() for p in note.split("\n\n") if p.strip()]
    if paras and paras[0] in ("Author’s Note", "Author's Note"):
        paras = paras[1:]
    return paras


# ---------------------------------------------------------------- EPUB

def _xhtml(title: str, body: str, lang: str) -> str:
    return (f'<?xml version="1.0" encoding="utf-8"?>\n'
            f'<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" '
            f'xml:lang="{lang}" lang="{lang}">\n<head><title>{html.escape(title)}</title>'
            f'<link rel="stylesheet" type="text/css" href="style.css"/></head>\n<body>\n{body}\n</body>\n</html>\n')


def _para_html(p: str) -> str:
    if p == SCENE_BREAK:
        return f'<p class="break">{SCENE_BREAK}</p>'
    text = ITALIC.sub(r"<em>\1</em>", html.escape(p, quote=False)).replace("\n", "<br/>")
    return f"<p>{text}</p>"


CSS = """body { font-family: serif; line-height: 1.5; }
h1 { font-size: 1.5em; margin: 2em 0 1em 0; text-align: center; }
p { text-indent: 1.2em; margin: 0; }
p.break, p.center { text-indent: 0; text-align: center; margin: 1em 0; }
"""


def build_epub(book: Book, out: Path) -> Path:
    out = Path(out)
    files: list[tuple[str, str, str]] = []   # (id, href, xhtml)
    lang = book.language
    title_body = [f"<h1>{html.escape(book.title)}</h1>"]
    if book.series:
        title_body.append(f'<p class="center">{html.escape(book.series)}</p>')
    title_body.append(f'<p class="center">{html.escape(book.author)}</p>')
    files.append(("title", "title.xhtml", _xhtml(book.title, "\n".join(title_body), lang)))
    for ch in book.chapters:
        heading = f"Chapter {ch.index}: {ch.title}"
        body = f"<h1>{html.escape(heading)}</h1>\n" + "\n".join(_para_html(p) for p in ch.paragraphs)
        files.append((f"chap{ch.index}", f"chapter_{ch.index}.xhtml", _xhtml(heading, body, lang)))
    if book.note:
        body = "<h1>Author’s Note</h1>\n" + "\n".join(_para_html(p) for p in _note_paragraphs(book.note))
        files.append(("author-note", "author-note.xhtml", _xhtml("Author’s Note", body, lang)))

    nav_items = "\n".join(f'<li><a href="{href}">{html.escape(f"Chapter {c.index}: {c.title}")}</a></li>'
                          for c, (_, href, _) in zip(book.chapters, files[1:]))
    nav = _xhtml("Contents", f'<nav epub:type="toc" id="toc"><h1>Contents</h1><ol>\n{nav_items}\n</ol></nav>', lang)
    manifest = "\n".join(f'<item id="{i}" href="{h}" media-type="application/xhtml+xml"/>' for i, h, _ in files)
    spine = "\n".join(f'<itemref idref="{i}"/>' for i, _, _ in files)
    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:identifier id="bookid">{book.identifier}</dc:identifier>
<dc:title>{html.escape(book.title)}</dc:title>
<dc:creator>{html.escape(book.author)}</dc:creator>
<dc:language>{lang}</dc:language>
<meta property="dcterms:modified">2000-01-01T00:00:00Z</meta>
</metadata>
<manifest>
<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
<item id="css" href="style.css" media-type="text/css"/>
{manifest}
</manifest>
<spine>
{spine}
</spine>
</package>
"""
    container = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                 '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
                 '<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>'
                 '</rootfiles></container>\n')
    with zipfile.ZipFile(out, "w") as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/content.opf", opf, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/nav.xhtml", nav, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/style.css", CSS, compress_type=zipfile.ZIP_DEFLATED)
        for _, href, xhtml in files:
            z.writestr(f"OEBPS/{href}", xhtml, compress_type=zipfile.ZIP_DEFLATED)
    return out


# ---------------------------------------------------------------- RTF

def _rtf(text: str) -> str:
    text = text.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}")
    if text != SCENE_BREAK:
        text = ITALIC.sub(r"{\\i \1}", text)
    text = text.replace("\n", r"\line ")
    # RTF is 7-bit: write non-ASCII characters as \uN? escapes.
    return "".join(ch if ord(ch) < 128 else f"\\u{ord(ch) if ord(ch) < 32768 else ord(ch) - 65536}?" for ch in text)


def build_rtf(book: Book, out: Path) -> Path:
    parts = [r"{\rtf1\ansi\deff0{\fonttbl{\f0 Times New Roman;}}\fs24 "]
    parts.append(r"\qc{\b\fs36 " + _rtf(book.title) + r"}\par ")
    if book.series:
        parts.append(_rtf(book.series) + r"\par ")
    parts.append(_rtf(book.author) + r"\par\ql ")
    sections = [(f"Chapter {c.index}: {c.title}", c.paragraphs) for c in book.chapters]
    if book.note:
        sections.append(("Author’s Note", _note_paragraphs(book.note)))
    for heading, paras in sections:
        parts.append(r"\page\qc{\b\fs28 " + _rtf(heading) + r"}\par\par\ql ")
        for p in paras:
            align = r"\qc " if p == SCENE_BREAK else r"\ql\fi360 "
            parts.append(align + _rtf(p) + r"\par ")
    parts.append("}")
    Path(out).write_text("".join(parts), encoding="ascii")
    return Path(out)


# ---------------------------------------------------------------- PDF

def _find_font(names: tuple[str, ...]) -> str | None:
    for d in FONT_DIRS:
        for n in names:
            p = Path(d) / n
            if p.is_file():
                return str(p)
    return None


def build_pdf(book: Book, out: Path, regular: str | None = None, bold: str | None = None,
              italic: str | None = None) -> Path:
    """6x9 inch reading PDF. Italics are kept when an italic font is available, else shown upright."""
    from fpdf import FPDF  # optional dependency: pip install fpdf2

    regular = regular or _find_font(("DejaVuSerif.ttf", "Georgia.ttf", "georgia.ttf"))
    bold = bold or _find_font(("DejaVuSerif-Bold.ttf", "Georgia Bold.ttf", "georgiab.ttf")) or regular
    italic = italic or _find_font(("DejaVuSerif-Italic.ttf", "Georgia Italic.ttf", "georgiai.ttf"))
    if not regular:
        raise RuntimeError("no Unicode serif font found; pass regular= (a .ttf path), e.g. DejaVuSerif.ttf")

    pdf = FPDF(format=(432, 648), unit="pt")
    pdf.set_margins(54, 54, 54)
    pdf.set_auto_page_break(auto=True, margin=54)
    pdf.add_font("Body", "", regular)
    pdf.add_font("Body", "B", bold)
    if italic:
        pdf.add_font("Body", "I", italic)

    def para(text: str, size: float = 11.5, align: str = "J"):
        pdf.set_font("Body", size=size)
        if text == SCENE_BREAK:
            pdf.ln(6)
            pdf.multi_cell(0, size * 1.45, SCENE_BREAK, align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(6)
            return
        if italic:
            # fpdf2 markdown: __text__ is italics. Escape stray underscores first.
            text = ITALIC.sub(r"__\1__", text.replace("__", "_ _"))
        else:
            text = ITALIC.sub(r"\1", text)
        pdf.multi_cell(0, size * 1.45, "    " + text, align=align, markdown=bool(italic), new_x="LMARGIN", new_y="NEXT")

    pdf.add_page()
    pdf.ln(150)
    pdf.set_font("Body", "B", 24)
    pdf.multi_cell(0, 30, book.title, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(12)
    pdf.set_font("Body", size=12)
    for line in filter(None, (book.series, book.author)):
        pdf.multi_cell(0, 18, line, align="C", new_x="LMARGIN", new_y="NEXT")

    sections = [(f"Chapter {c.index}: {c.title}", c.paragraphs) for c in book.chapters]
    if book.note:
        sections.append(("Author’s Note", _note_paragraphs(book.note)))
    for heading, paras in sections:
        pdf.add_page()
        pdf.ln(60)
        pdf.set_font("Body", "B", 16)
        pdf.multi_cell(0, 22, heading, align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(18)
        for p in paras:
            para(p)
    pdf.output(str(out))
    return Path(out)
