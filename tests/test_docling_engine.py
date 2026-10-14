"""Docling engine behaviour. Needs the docling extra; skipped otherwise."""

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

pytest.importorskip("docling")

from ai_doc2md import cli, docling_engine  # noqa: E402
from ai_doc2md.errors import ConversionError  # noqa: E402


def make_pdf(path: Path, text: str | None = None) -> None:
    """Write a one-page PDF with the given ASCII text, or a blank page if text is None."""
    content = f"BT /F1 24 Tf 72 700 Td ({text}) Tj ET" if text else ""
    objects = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        "/Resources << /Font << /F1 5 0 R >> >> >>",
        f"<< /Length {len(content)} >>\nstream\n{content}\nendstream",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = "%PDF-1.4\n"
    offsets = []
    for number, body in enumerate(objects, 1):
        offsets.append(len(out.encode("latin-1")))
        out += f"{number} 0 obj\n{body}\nendobj\n"
    xref = len(out.encode("latin-1"))
    out += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n"
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n"
    out += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n"
    path.write_bytes(out.encode("latin-1"))


def _args(path: Path, out: Path, **overrides):
    base = dict(
        input=str(path),
        output=str(out),
        engine="auto",
        device="cpu",
        keep_repeated_headers=False,
        ocr="auto",
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def test_text_pdf_does_not_need_ocr(tmp_path):
    pdf = tmp_path / "text.pdf"
    make_pdf(pdf, text="This page has a real text layer with plenty of characters on it")
    assert docling_engine.pdf_needs_ocr(pdf) is False


def test_blank_pdf_needs_ocr(tmp_path):
    pdf = tmp_path / "blank.pdf"
    make_pdf(pdf, text=None)
    assert docling_engine.pdf_needs_ocr(pdf) is True


def test_unreadable_pdf_defaults_to_ocr(tmp_path):
    pdf = tmp_path / "broken.pdf"
    pdf.write_bytes(b"not a pdf")
    assert docling_engine.pdf_needs_ocr(pdf) is True


def test_text_pdf_converts_with_text_and_no_placeholders(tmp_path):
    pdf = tmp_path / "text.pdf"
    make_pdf(pdf, text="Sample sentence that Docling should read from the text layer")
    out = tmp_path / "out" / "text.md"

    assert cli._convert(_args(pdf, out)) == 0

    md = out.read_text(encoding="utf-8")
    assert "Sample sentence" in md
    assert "<!-- image -->" not in md
    assert not (out.parent / "text-media").exists()


def test_missing_docling_gives_a_clear_message(tmp_path, monkeypatch, capsys):
    pdf = tmp_path / "scan.pdf"
    make_pdf(pdf, text="x")
    for name in list(sys.modules):
        if name == "docling" or name.startswith("docling."):
            monkeypatch.delitem(sys.modules, name)
    monkeypatch.setitem(sys.modules, "docling", None)

    with pytest.raises(ConversionError, match="ai-doc2md\\[docling\\]"):
        docling_engine.convert(pdf, tmp_path / "scan.md")


def test_invalid_ocr_mode_is_rejected(tmp_path):
    pdf = tmp_path / "text.pdf"
    make_pdf(pdf, text="x")
    with pytest.raises(ValueError):
        docling_engine.convert(pdf, tmp_path / "text.md", ocr="sometimes")
