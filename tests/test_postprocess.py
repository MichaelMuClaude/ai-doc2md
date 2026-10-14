from ai_doc2md.postprocess import unwrap_internal_links


def test_internal_xhtml_link_keeps_only_its_text():
    md = "See the note [3](../Text/page_1_split_0.xhtml#abc123) for details."
    assert unwrap_internal_links(md) == "See the note 3 for details."


def test_escaped_bracket_link_text_is_kept():
    md = "claim[\\[9\\]](../Text/page_23_split_0.xhtml#88bd)"
    assert unwrap_internal_links(md) == "claim\\[9\\]"


def test_external_and_image_links_are_untouched():
    md = "[site](https://example.com) and ![cover](book-media/cover.jpg)"
    assert unwrap_internal_links(md) == md


def test_plain_text_is_untouched():
    md = "# Heading\n\nPlain paragraph with [brackets] and (parens)."
    assert unwrap_internal_links(md) == md


def test_first_level_two_heading_becomes_the_title():
    from ai_doc2md.postprocess import promote_title

    md = "## Report\n\nIntro text.\n\n## Findings\n\nMore."
    assert promote_title(md) == "# Report\n\nIntro text.\n\n## Findings\n\nMore."


def test_existing_level_one_heading_is_left_alone():
    from ai_doc2md.postprocess import promote_title

    md = "# Book\n\n## Chapter\n"
    assert promote_title(md) == md


def test_document_without_headings_is_left_alone():
    from ai_doc2md.postprocess import promote_title

    md = "Just a paragraph."
    assert promote_title(md) == md
