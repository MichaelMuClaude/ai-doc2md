# Contributing to ai-doc2md

Thanks for helping. Humans and AI agents are both welcome. The detailed rules for agents are in [AGENTS.md](AGENTS.md).

## Ground rules

- Keep conversion local: no cloud APIs and no uploads of document content.
- Never remove content silently. Filtering must always be reported.
- Use synthetic test data only. Do not commit real documents or their output.
- Keep changes small, and add a test for every behaviour change.

## Running the tests

```bash
sudo apt install pandoc
python3 -m venv ~/.venvs/ai-doc2md-dev
~/.venvs/ai-doc2md-dev/bin/pip install -e ".[docling,dev]"
~/.venvs/ai-doc2md-dev/bin/python -m pytest -q
```

The first install downloads PyTorch, so it takes a while. Continuous integration runs the same suite on Python 3.10 and 3.13.

## Adding a document format

Edit the routing table in `src/ai_doc2md/formats.py`, add a routing test, and update the README. [AGENTS.md](AGENTS.md#adding-a-format) has the full checklist.

## Opening a pull request

1. Fork the repository and create a branch with a descriptive name.
2. Make the change with tests.
3. Describe what changed, why, and which tests you ran.
4. If an AI agent wrote or helped write the change, say so and name the tool and model.

## Reporting bugs

Open an issue with the command, the output you got, and the output you expected. Describe the file type and its general layout. Do not attach a real document. If you need to show a problem, make a synthetic file that reproduces it.

## Licence

By contributing, you agree that your contribution is released under the MIT licence in [LICENSE](LICENSE).
