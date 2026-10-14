import argparse
import sys
from pathlib import Path

from ai_doc2md import __version__
from ai_doc2md import docling_engine, pandoc_engine
from ai_doc2md.formats import ENGINES, UnsupportedFormatError, engine_for
from ai_doc2md.pandoc_engine import ConversionError


def _convert(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"error: no such file: {input_path}", file=sys.stderr)
        return 1

    try:
        engine = engine_for(input_path, getattr(args, "engine", "auto"))
    except UnsupportedFormatError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    output_path = Path(args.output) if args.output else input_path.with_suffix(".md")
    try:
        if engine == "pandoc":
            pandoc_engine.convert(input_path, output_path)
        else:
            docling_engine.convert(
                input_path,
                output_path,
                device=getattr(args, "device", "cpu"),
                keep_repeated_headers=getattr(args, "keep_repeated_headers", False),
            )
    except ConversionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"wrote {output_path}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ai-doc2md",
        description="Convert documents (PDF, EPUB, DOCX, HTML, slides, spreadsheets, images) to Markdown",
    )
    parser.add_argument("--version", action="version", version=__version__)

    subparsers = parser.add_subparsers(dest="command", required=True)

    convert_parser = subparsers.add_parser("convert", help="Convert a document to Markdown")
    convert_parser.add_argument("input", help="Path to the input file")
    convert_parser.add_argument(
        "-o", "--output", help="Output .md path (default: same name as input, .md extension)"
    )
    convert_parser.add_argument(
        "--engine",
        choices=ENGINES,
        default="auto",
        help="auto picks pandoc for text formats (EPUB, DOCX, HTML, ODT, RTF, LaTeX) and "
        "Docling for everything else; pandoc or docling forces one engine",
    )
    convert_parser.add_argument(
        "--device",
        choices=["cpu", "cuda", "auto"],
        default="cpu",
        help="Device for Docling's models (default: cpu). Ignored by pandoc.",
    )
    convert_parser.add_argument(
        "--keep-repeated-headers",
        action="store_true",
        help="Docling only: do not filter repeated running headers/footers (filtering is on by default)",
    )
    convert_parser.set_defaults(func=_convert)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
