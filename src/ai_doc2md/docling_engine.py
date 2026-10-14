"""Convert documents with Docling: PDFs, scans, slides, spreadsheets, and images."""

import os
from pathlib import Path

from ai_doc2md.errors import ConversionError
from ai_doc2md.postprocess import promote_title

OCR_MODES = ("auto", "on", "off")

# A page with fewer characters than this in its text layer is treated as a scan.
MIN_TEXT_CHARS_PER_PAGE = 20


def pdf_needs_ocr(path: Path) -> bool:
    """Return True if any page of the PDF has no usable text layer.

    If the file cannot be read, return True: OCR is the safe default.
    """
    try:
        import pypdfium2 as pdfium
    except ImportError:
        return True
    try:
        pdf = pdfium.PdfDocument(str(path))
    except Exception:
        return True
    try:
        for index in range(len(pdf)):
            text = pdf[index].get_textpage().get_text_range().strip()
            if len(text) < MIN_TEXT_CHARS_PER_PAGE:
                return True
        return False
    finally:
        pdf.close()


def convert(
    input_path: Path,
    output_path: Path,
    device: str = "cpu",
    keep_repeated_headers: bool = False,
    ocr: str = "auto",
) -> None:
    if ocr not in OCR_MODES:
        raise ValueError(f"ocr must be one of {OCR_MODES}, not {ocr!r}")

    # Imported here so that pandoc-only conversions never load PyTorch.
    try:
        from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.document_converter import DocumentConverter, PdfFormatOption
        from docling_core.types.doc import ImageRefMode
    except ImportError as exc:
        raise ConversionError(
            "Docling is not installed. For PDFs, slides, spreadsheets and images, run: "
            "pip install 'ai-doc2md[docling]'"
        ) from exc

    from ai_doc2md.furniture import filter_running_furniture, format_note

    accelerator = {
        "cpu": AcceleratorDevice.CPU,
        "cuda": AcceleratorDevice.CUDA,
        "auto": AcceleratorDevice.AUTO,
    }[device]

    is_pdf = input_path.suffix.lower() == ".pdf"
    if is_pdf:
        do_ocr = ocr == "on" or (ocr == "auto" and pdf_needs_ocr(input_path))
    else:
        do_ocr = True  # other formats use their own pipelines; this value is not used

    pipeline_options = PdfPipelineOptions(do_ocr=do_ocr, generate_picture_images=True)
    pipeline_options.accelerator_options = AcceleratorOptions(
        device=accelerator, num_threads=os.cpu_count() or 4
    )

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
        }
    )
    document = converter.convert(str(input_path)).document

    filtered = []
    if not keep_repeated_headers:
        filtered = filter_running_furniture(document)

    # Docling writes picture files and links them. Use an absolute folder so the
    # links can be rewritten to paths relative to the Markdown file.
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    media_name = f"{output_path.stem}-media"
    media_dir = output_path.parent / media_name
    document.save_as_markdown(
        output_path,
        artifacts_dir=media_dir,
        image_mode=ImageRefMode.REFERENCED,
        image_placeholder="",
    )
    markdown = output_path.read_text(encoding="utf-8")
    markdown = markdown.replace(str(media_dir) + "/", media_name + "/")
    if media_dir.is_dir() and not any(media_dir.iterdir()):
        media_dir.rmdir()
    markdown = promote_title(markdown)

    if filtered:
        note = format_note(filtered)
        markdown = note + "\n\n" + markdown
        print(note)

    output_path.write_text(markdown, encoding="utf-8")
