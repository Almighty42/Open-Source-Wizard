from bs4 import BeautifulSoup, Tag

from .blockquotes import transform_blockquotes
from .codeblocks import transform_code_block
from .heading import group_by_headings

def group_article_content(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    factory = BeautifulSoup("", "html.parser")

    transform_blockquotes(soup, factory) 
    transform_code_block(soup, factory)

    elements = [el for el in soup.contents if isinstance(el, Tag)]
    result = group_by_headings(elements, factory)
    return str(result)
