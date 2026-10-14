"""Clean-up applied to Markdown produced by pandoc."""

import re

# [text](../Text/page_1.xhtml#id) -> text
# EPUB-internal targets do not exist in the Markdown output, so keep only the text.
# The link text may contain escaped brackets such as \[9\].
_INTERNAL_LINK = re.compile(r"\[((?:\\.|[^\]\\])*)\]\([^)]*\.xhtml[^)]*\)")


def unwrap_internal_links(markdown: str) -> str:
    return _INTERNAL_LINK.sub(r"\1", markdown)
