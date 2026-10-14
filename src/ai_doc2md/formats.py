"""Map input file extensions to the conversion engine that handles them best."""

from pathlib import Path

# Text-based formats that pandoc converts quickly and faithfully.
PANDOC_EXTENSIONS = {".epub", ".docx", ".odt", ".rtf", ".html", ".htm", ".tex", ".latex"}

# Formats only Docling reads, plus Docling's own handling of the PANDOC formats.
DOCLING_ONLY_EXTENSIONS = {
    ".doc",
    ".ppt",
    ".pptx",
    ".xls",
    ".xlsx",
    ".ods",
    ".odp",
    ".csv",
    ".png",
    ".jpg",
    ".jpeg",
    ".tif",
    ".tiff",
    ".bmp",
    ".webp",
}

ENGINES = ("auto", "pandoc", "docling")

# PDFs are handled by the ai-pdf tool, which owns qpdf and PDF-to-Markdown.
PDF_EXTENSIONS = {".pdf"}


class UnsupportedFormatError(ValueError):
    pass


def engine_for(path: Path, engine: str = "auto") -> str:
    """Return "pandoc" or "docling" for this file.

    ``engine`` lets the caller force one engine. Forcing pandoc on a format it
    cannot read is an error, not a silent fallback.
    """
    if engine not in ENGINES:
        raise UnsupportedFormatError(f"unknown engine: {engine}")

    ext = path.suffix.lower()
    if ext in PDF_EXTENSIONS:
        if engine in ("auto", "pdf"):
            return "pdf"
        raise UnsupportedFormatError("PDFs are converted by ai-pdf; use --engine auto")
    pandoc_ok = ext in PANDOC_EXTENSIONS
    docling_ok = pandoc_ok or ext in DOCLING_ONLY_EXTENSIONS

    if engine == "pandoc":
        if not pandoc_ok:
            raise UnsupportedFormatError(f"pandoc cannot read {ext or 'files without an extension'}")
        return "pandoc"
    if engine == "docling":
        if not docling_ok:
            raise UnsupportedFormatError(f"unsupported file type: {ext or 'no extension'}")
        return "docling"

    if pandoc_ok:
        return "pandoc"
    if ext in DOCLING_ONLY_EXTENSIONS:
        return "docling"
    raise UnsupportedFormatError(f"unsupported file type: {ext or 'no extension'}")
