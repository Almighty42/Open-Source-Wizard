import re
import markdown
import bleach
from bs4 import BeautifulSoup

from .markdown import group_article_content
from .sanitize import ALLOWED_TAGS, ALLOWED_ATTRIBUTES

def render_markdown(val):
    if not val:
        return ""
    html = markdown.markdown(
        val,
        extensions=["fenced_code", "tables", "toc"],
    )
    def preserve_blank_lines(m):
        return m.group(0).replace("\n\n", "\n \n")
    html = re.sub(r'<pre><code[^>]*>.*?</code></pre>', preserve_blank_lines, html, flags=re.DOTALL)
    
    html = group_article_content(html)
    return bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)

def format_date(val):
    if val is None:
        return ""
    return val.strftime("%d %b %y").upper()

def extract_headings(body: str) -> list[dict]:
    body_no_code = re.sub(r'```.*?```', '', body, flags=re.DOTALL)
    html = markdown.markdown(body_no_code)
    soup = BeautifulSoup(html, "html.parser")
    return [
        {
            "text": h1.get_text(strip=True),
            "id": h1.get_text(strip=True).lower().strip().replace(" ", "-").replace("/", "-")
        }
        for h1 in soup.find_all("h1")
    ]
