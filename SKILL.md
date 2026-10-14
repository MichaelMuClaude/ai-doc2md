---
name: ai-doc2md
description: Convert common documents (EPUB, Word, OpenDocument, HTML, LaTeX, PowerPoint, Excel, images) to Markdown so an agent can read them. For PDFs, use ai-pdf instead. Use for batch conversion or when the file is too large to read directly. Runs locally; no cloud API.
---

# ai-doc2md

## What it does

Converts one document to a Markdown file. The engine is chosen from the file extension:

- **pandoc** for EPUB, DOCX, ODT, RTF, HTML, and LaTeX. Fast.
- **Docling** for DOC, PPT, PPTX, XLS, XLSX, ODS, ODP, CSV, and images. Slower. Images are read with OCR.
- **PDFs are not handled here.** Use `ai-pdf to-markdown` for them.

## Usage

```bash
ai-doc2md convert input.epub                 # writes input.md and input-media/
ai-doc2md convert input.pptx -o out/input.md  # choose the output path
ai-doc2md convert input.pptx --engine docling
ai-doc2md convert slides.pptx --keep-repeated-headers
```

- **Success:** exit code 0, and the output path is printed.
- **Unsupported file type:** exit code 2 and a message on stderr.
- **Other failures:** exit code 1 and a message on stderr. A missing pandoc or a missing Docling install is reported this way.

## Output

- A `.md` file next to the input, or at the `-o` path.
- Images, when present, in `<name>-media/` beside the Markdown file. Links in the Markdown are relative, so the pair can be moved together.

## Choosing when to use it

- Use it for batch conversion, or when a document is large and you need a text version to search or summarise.
- For a short document you can read directly, reading it directly is often quicker.

## Known limits

- Headings: the first heading becomes level 1 and the rest level 2. Check the outline before relying on it.
- Images are read with OCR, which can misread characters.
- Pictures from Docling output are saved in `<name>-media/` and linked.
- Maths appears as LaTeX inside `$...$`.
- DRM-protected files cannot be converted.
