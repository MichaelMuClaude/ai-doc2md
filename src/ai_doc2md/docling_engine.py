"""Convert documents with Docling: PDFs, scans, slides, spreadsheets, and images."""

from pathlib import Path


def convert(
    input_path: Path,
    output_path: Path,
    device: str = "cpu",
    keep_repeated_headers: bool = False,
) -> None:
    # Imported here so that pandoc-only conversions never load PyTorch.
    from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption

    from ai_doc2md.furniture import filter_running_furniture, format_note

    accelerator = {
        "cpu": AcceleratorDevice.CPU,
        "cuda": AcceleratorDevice.CUDA,
        "auto": AcceleratorDevice.AUTO,
    }[device]

    pipeline_options = PdfPipelineOptions()
    pipeline_options.accelerator_options = AcceleratorOptions(device=accelerator)

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
        }
    )
    result = converter.convert(str(input_path))

    filtered = []
    if not keep_repeated_headers:
        filtered = filter_running_furniture(result.document)

    markdown = result.document.export_to_markdown()
    if filtered:
        note = format_note(filtered)
        markdown = note + "\n\n" + markdown
        print(note)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
