"""Real Docling conversions of small generated files. Skipped when Docling is not installed."""

import csv

import pytest

pytest.importorskip("docling")

from ai_doc2md import cli  # noqa: E402


def _args(path, out):
    from types import SimpleNamespace

    return SimpleNamespace(
        input=str(path),
        output=str(out),
        engine="auto",
        device="cpu",
        keep_repeated_headers=False,
    )


def test_csv_converts_to_a_table(tmp_path):
    source = tmp_path / "sample.csv"
    with source.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Item", "Value"])
        writer.writerow(["Alpha", 12])
    out = tmp_path / "sample.md"

    assert cli._convert(_args(source, out)) == 0
    md = out.read_text(encoding="utf-8")
    assert "Alpha" in md and "12" in md


def test_xlsx_converts_to_a_table(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    source = tmp_path / "sample.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Item", "Value"])
    ws.append(["Beta", 34])
    wb.save(source)
    out = tmp_path / "sample.md"

    assert cli._convert(_args(source, out)) == 0
    md = out.read_text(encoding="utf-8")
    assert "Beta" in md and "34" in md


def test_pptx_converts_title_and_bullets(tmp_path):
    pptx = pytest.importorskip("pptx")
    source = tmp_path / "slides.pptx"
    prs = pptx.Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Sample Slide Title"
    slide.placeholders[1].text = "First bullet point\nSecond bullet point"
    prs.save(source)
    out = tmp_path / "slides.md"

    assert cli._convert(_args(source, out)) == 0
    md = out.read_text(encoding="utf-8")
    assert "Sample Slide Title" in md
    assert "First bullet point" in md
