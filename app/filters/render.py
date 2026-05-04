import re
import markdown
import bleach
from bs4 import BeautifulSoup

from .markdown import group_article_content
from .sanitize import ALLOWED_TAGS, ALLOWED_ATTRIBUTES
from .assets import resolve_asset_images

def render_markdown(val, article_assets=None):
    if not val:
        return ""
    if article_assets:
        val = resolve_asset_images(val, article_assets)
    html = markdown.markdown(
        val,
        extensions=["fenced_code", "tables", "toc"],
    )

    def preserve_blank_lines(m):
        return m.group(0).replace("\n\n", "\n \n")
    html = re.sub(r'<pre><code[^>]*>.*?</code></pre>', preserve_blank_lines, html, flags=re.DOTALL)
    
    html = bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
    html = group_article_content(html)
    return html

def format_date(val):
    if val is None:
        return ""
    return val.strftime("%d %b %y").upper()

def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)   
    text = re.sub(r'[\s_]+', '-', text)   
    text = re.sub(r'-+', '-', text)      
    return text

def extract_headings(body: str) -> list[dict]:
    body_no_code = re.sub(r'```.*?```', '', body, flags=re.DOTALL)
    html = markdown.markdown(body_no_code)
    soup = BeautifulSoup(html, "html.parser")
    return [
        {
            "text": h1.get_text(strip=True),
            "id": _slugify(h1.get_text(strip=True))
        }
        for h1 in soup.find_all("h1")
    ]


def replace_arg(args, key, value):
    d = args.to_dict(flat=False)
    d[key] = [value]
    from urllib.parse import urlencode
    return urlencode(d, doseq=True)
