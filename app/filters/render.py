import re
from urllib.parse import urlencode

import bleach
import markdown
from bs4 import BeautifulSoup

from .assets import resolve_asset_images
from .heading import shift_headings, top_level_tags, assign_heading_ids, collect_outline
from .markdown import group_article_content
from .sanitize import ALLOWED_TAGS, ALLOWED_ATTRIBUTES

MD_EXTENSIONS = ["fenced_code", "tables"]


def _markdown_to_clean_html(val: str) -> str:
    html = markdown.markdown(val, extensions=MD_EXTENSIONS)

    def preserve_blank_lines(m):
        return m.group(0).replace("\n\n", "\n \n")
    html = re.sub(r'<pre><code[^>]*>.*?</code></pre>', preserve_blank_lines, html, flags=re.DOTALL)

    return bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)


def render_markdown(val, article_assets=None):
    if not val:
        return ""
    if article_assets:
        val = resolve_asset_images(val, article_assets)
    return group_article_content(_markdown_to_clean_html(val))


def format_date(val):
    if val is None:
        return ""
    return val.strftime("%d %b %y").upper()


def extract_headings(body: str) -> list[dict]:
    if not body:
        return []
    soup = BeautifulSoup(_markdown_to_clean_html(body), "html.parser")
    shift_headings(soup)
    elements = top_level_tags(soup)
    assign_heading_ids(elements)
    return collect_outline(elements)


def replace_arg(args, key, value):
    d = args.to_dict(flat=False)
    d[key] = [value]
    return urlencode(d, doseq=True)
