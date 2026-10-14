"""Convert text-based documents with pandoc."""

import shutil
import subprocess
from pathlib import Path

from ai_doc2md.postprocess import unwrap_internal_links


class ConversionError(RuntimeError):
    pass


def convert(input_path: Path, output_path: Path) -> None:
    """Write Markdown for ``input_path`` to ``output_path``.

    Images are extracted into ``<output stem>-media/`` next to the output file.
    pandoc runs from the output folder so that image links are relative to the
    Markdown file, not to wherever the command was started.
    """
    pandoc = shutil.which("pandoc")
    if pandoc is None:
        raise ConversionError("pandoc is not installed (on Ubuntu: sudo apt install pandoc)")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    media_dir = f"{output_path.stem}-media"
    cmd = [
        pandoc,
        str(input_path.resolve()),
        "-t",
        "gfm-raw_html",
        "--wrap=none",
        "--extract-media",
        media_dir,
        "-o",
        output_path.name,
    ]
    result = subprocess.run(cmd, cwd=output_path.resolve().parent, capture_output=True, text=True)
    if result.returncode != 0:
        raise ConversionError(f"pandoc failed: {result.stderr.strip() or 'no error output'}")

    markdown = output_path.read_text(encoding="utf-8")
    output_path.write_text(unwrap_internal_links(markdown), encoding="utf-8")
