import markdown
import bleach
from bs4 import BeautifulSoup, Tag

from .sanitize import ALLOWED_TAGS, ALLOWED_ATTRIBUTES
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

def render_markdown(val: str) -> str:
    if not val:
        return ""

    html = markdown.markdown(val, extensions=["fenced_code", "tables", "toc"])
    html = bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
    html = group_article_content(html)
    return html
