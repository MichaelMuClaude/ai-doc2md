import subprocess
import sys
from types import SimpleNamespace

from ai_doc2md import cli, docling_engine, pandoc_engine


def _args(**overrides):
    base = dict(input="", output=None, engine="auto", device="cpu", keep_repeated_headers=False)
    base.update(overrides)
    return SimpleNamespace(**base)


def test_pdf_is_routed_to_docling(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(docling_engine, "convert", lambda *a, **k: calls.append(("docling", a, k)))
    monkeypatch.setattr(pandoc_engine, "convert", lambda *a, **k: calls.append(("pandoc", a, k)))

    source = tmp_path / "scan.pdf"
    source.write_bytes(b"%PDF-1.4 fake")
    assert cli._convert(_args(input=str(source), output=str(tmp_path / "scan.md"))) == 0
    assert calls and calls[0][0] == "docling"


def test_epub_is_routed_to_pandoc(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(docling_engine, "convert", lambda *a, **k: calls.append("docling"))
    monkeypatch.setattr(pandoc_engine, "convert", lambda *a, **k: calls.append("pandoc"))

    source = tmp_path / "book.epub"
    source.write_bytes(b"not really an epub")
    assert cli._convert(_args(input=str(source))) == 0
    assert calls == ["pandoc"]


def test_forced_engine_is_respected(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(docling_engine, "convert", lambda *a, **k: calls.append("docling"))
    monkeypatch.setattr(pandoc_engine, "convert", lambda *a, **k: calls.append("pandoc"))

    source = tmp_path / "book.epub"
    source.write_bytes(b"x")
    assert cli._convert(_args(input=str(source), engine="docling")) == 0
    assert calls == ["docling"]


def test_unsupported_extension_exits_with_code_2(tmp_path, capsys):
    source = tmp_path / "archive.zip"
    source.write_bytes(b"x")
    assert cli._convert(_args(input=str(source))) == 2
    assert "unsupported file type" in capsys.readouterr().err


def test_missing_input_exits_with_code_1(tmp_path, capsys):
    assert cli._convert(_args(input=str(tmp_path / "nope.pdf"))) == 1
    assert "no such file" in capsys.readouterr().err


def test_version_flag():
    result = subprocess.run(
        [sys.executable, "-m", "ai_doc2md.cli", "--version"], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "0.1.0" in result.stdout
