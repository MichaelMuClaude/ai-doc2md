"""Docling engine: the friendly message when Docling is missing."""

import sys
from pathlib import Path

import pytest

from ai_doc2md import docling_engine
from ai_doc2md.errors import ConversionError


def test_missing_docling_gives_a_clear_message(tmp_path, monkeypatch):
    for name in list(sys.modules):
        if name == "docling" or name.startswith("docling."):
            monkeypatch.delitem(sys.modules, name)
    monkeypatch.setitem(sys.modules, "docling", None)
    source = tmp_path / "slides.pptx"
    source.write_bytes(b"x")

    with pytest.raises(ConversionError, match="ai-doc2md\\[docling\\]"):
        docling_engine.convert(Path(source), tmp_path / "slides.md")
