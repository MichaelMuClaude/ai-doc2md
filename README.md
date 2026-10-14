# ai-doc2md

Convert a document to Markdown, so that AI models can read it. Works with EPUB, Word, OpenDocument, HTML, LaTeX, PowerPoint, Excel, and images. **PDFs are handled by [ai-pdf](https://github.com/MichaelMuClaude/ai-pdf)**, which also uses qpdf for checking, repairing, merging, and splitting PDFs.

```bash
ai-doc2md convert book.epub             # writes book.md and book-media/
ai-doc2md convert slides.pptx           # writes slides.md
ai-doc2md convert slides.pptx -o out/slides.md
```

The tool picks the conversion engine from the file extension:

| Engine | Used for | Notes |
|---|---|---|
| [pandoc](https://pandoc.org) | EPUB, DOCX, ODT, RTF, HTML, LaTeX | Very fast, about 0.2 seconds for a 16 MB book. Needs pandoc installed. |
| [Docling](https://github.com/docling-project/docling) | DOC, PPT, PPTX, XLS, XLSX, ODS, ODP, CSV, images | Uses local vision models to keep headings, tables, and lists. Slower, and heavy to install. |

You can force an engine with `--engine pandoc` or `--engine docling`. Forcing pandoc on a format it cannot read is an error.

## Output

- One Markdown file per input, next to the input unless `-o` is given.
- Images are saved in `<name>-media/` next to the Markdown file, and the links are relative, so the folder can be moved as a whole.
- Pandoc output keeps headings, lists, tables, and bold or italic text. EPUB-internal links are removed and their text is kept.
- Docling output removes repeated running headers and footers (for example a classification marking on every page). A note at the top of the file lists what was removed. Use `--keep-repeated-headers` to turn this off.
- Docling output saves pictures to `<name>-media/` and links them. The title becomes a level-1 heading when the document has none.
- PDFs are converted by `ai-pdf to-markdown`, which decides on OCR per file.
- `--device auto` lets Docling use a GPU when one is available. It is much faster (about 11 seconds instead of about 26 seconds for a 34-page report on the test machine), but it uses GPU memory. The default is `cpu`.

## Install

```bash
pip install -e .                  # text formats only (needs pandoc)
pip install -e ".[docling]"       # adds slides, spreadsheets, and images (large, installs PyTorch)
```

Install pandoc from your package manager, for example `sudo apt install pandoc`.

Requires Python 3.10 or newer.

## Limits

- Heading levels come from the source file. Some EPUBs have inconsistent heading levels, and the output keeps them. Check the outline for important documents.
- Images are read with OCR, which can misread characters, and Docling sometimes marks OCR text as a heading. Check the output against the image.
- Docling reports every heading with the same level, so the output makes the first heading level 1 and the rest level 2. If the first heading is a chapter rather than the title, it becomes level 1 too.
- Pictures are exported as separate files. Small decorative images can add many files, so check the `-media` folder.
- Maths is written as LaTeX inside `$...$`, which plain-text viewers show as raw code.
- DRM-protected files cannot be converted. Only convert files you have the right to convert.

## Third-party components

| Component | Purpose | Licence |
|---|---|---|
| pandoc | Converts text-based formats (called as an external program, not bundled) | GPL-2.0 (see pandoc's LICENSE) |
| Docling and its `docling-*` packages | Document pipeline (optional) | MIT |
| PyTorch, Transformers | Model runtime for Docling (optional) | Apache-2.0 |
| Models from Hugging Face (`docling-project/*`) | Downloaded at runtime by Docling | Check each model card |
| NVIDIA CUDA libraries (installed by PyTorch on Linux) | GPU support (optional) | NVIDIA proprietary licence |

Nothing here is bundled with this project. Users install these tools themselves.

## Development

```bash
python3 -m venv ~/.venvs/ai-doc2md-dev
~/.venvs/ai-doc2md-dev/bin/pip install -e ".[docling,dev]"
~/.venvs/ai-doc2md-dev/bin/python -m pytest -q
```

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md).

## Licence

MIT. See [LICENSE](LICENSE).
