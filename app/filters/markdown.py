from bs4 import BeautifulSoup

from .blockquotes import transform_blockquotes
from .codeblocks import transform_code_block
from .heading import group_by_headings, shift_headings, top_level_tags, assign_heading_ids

def group_article_content(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    factory = BeautifulSoup("", "html.parser")

    shift_headings(soup)
    transform_blockquotes(soup, factory)
    transform_code_block(soup, factory)

    elements = top_level_tags(soup)
    assign_heading_ids(elements)
    return str(group_by_headings(elements, factory))
