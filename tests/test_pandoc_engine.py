import base64
import re
import shutil
from pathlib import Path

import pytest

from ai_doc2md import pandoc_engine
from ai_doc2md.pandoc_engine import ConversionError

requires_pandoc = pytest.mark.skipif(shutil.which("pandoc") is None, reason="pandoc not installed")

# A 1x1 PNG, so the fixture can contain a real image without shipping a binary file.
PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
)

SAMPLE_MD = """# Chapter One

Some **bold** text and a table:

| a | b |
|---|---|
| 1 | 2 |

![a picture](pic.png)
"""


def _make_source(tmp_path: Path, fmt: str) -> Path:
    """Build a small EPUB or DOCX from Markdown with pandoc, for use as test input."""
    import subprocess

    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "pic.png").write_bytes(PNG_1X1)
    (src_dir / "sample.md").write_text(SAMPLE_MD, encoding="utf-8")
    target = src_dir / f"sample.{fmt}"
    subprocess.run(
        ["pandoc", "sample.md", "-o", target.name, "--resource-path", "."],
        cwd=src_dir,
        check=True,
        capture_output=True,
    )
    return target


@requires_pandoc
@pytest.mark.parametrize("fmt", ["epub", "docx"])
def test_converts_text_formats_to_markdown(tmp_path, fmt):
    source = _make_source(tmp_path, fmt)
    out = tmp_path / "out" / "result.md"

    pandoc_engine.convert(source, out)

    md = out.read_text(encoding="utf-8")
    assert "Chapter One" in md
    assert "**bold**" in md
    assert "|" in md  # the table survives


@requires_pandoc
def test_image_links_are_relative_to_the_markdown_file(tmp_path):
    source = _make_source(tmp_path, "epub")
    out = tmp_path / "out" / "result.md"

    pandoc_engine.convert(source, out)

    md = out.read_text(encoding="utf-8")
    links = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", md)
    assert links, "expected at least one image link"
    for link in links:
        assert not link.startswith("/"), "image links must not be absolute"
        assert (out.parent / link).is_file(), f"image link does not resolve: {link}"


@requires_pandoc
def test_no_internal_xhtml_links_in_output(tmp_path):
    source = _make_source(tmp_path, "epub")
    out = tmp_path / "out" / "result.md"

    pandoc_engine.convert(source, out)

    assert ".xhtml" not in out.read_text(encoding="utf-8")


def test_missing_pandoc_gives_a_clear_error(tmp_path, monkeypatch):
    monkeypatch.setattr(pandoc_engine.shutil, "which", lambda name: None)
    with pytest.raises(ConversionError, match="pandoc is not installed"):
        pandoc_engine.convert(tmp_path / "book.epub", tmp_path / "book.md")
