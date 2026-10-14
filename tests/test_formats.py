from pathlib import Path

import pytest

from ai_doc2md.formats import UnsupportedFormatError, engine_for


@pytest.mark.parametrize(
    "name, expected",
    [
        ("book.epub", "pandoc"),
        ("report.docx", "pandoc"),
        ("page.html", "pandoc"),
        ("page.htm", "pandoc"),
        ("notes.odt", "pandoc"),
        ("paper.tex", "pandoc"),
        ("scan.pdf", "docling"),
        ("legacy.doc", "docling"),
        ("deck.pptx", "docling"),
        ("sheet.xlsx", "docling"),
        ("photo.jpg", "docling"),
    ],
)
def test_auto_engine_by_extension(name, expected):
    assert engine_for(Path(name)) == expected


def test_extension_matching_is_case_insensitive():
    assert engine_for(Path("BOOK.EPUB")) == "pandoc"
    assert engine_for(Path("SCAN.PDF")) == "docling"


def test_unknown_extension_is_rejected():
    with pytest.raises(UnsupportedFormatError):
        engine_for(Path("archive.zip"))


def test_no_extension_is_rejected():
    with pytest.raises(UnsupportedFormatError):
        engine_for(Path("README"))


def test_forcing_pandoc_on_pdf_is_an_error_not_a_fallback():
    with pytest.raises(UnsupportedFormatError):
        engine_for(Path("scan.pdf"), "pandoc")


def test_forcing_docling_on_epub_is_allowed():
    assert engine_for(Path("book.epub"), "docling") == "docling"


def test_unknown_engine_name_is_rejected():
    with pytest.raises(UnsupportedFormatError):
        engine_for(Path("book.epub"), "magic")
