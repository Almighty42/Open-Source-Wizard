import markdown
import copy
import bleach
from bs4 import BeautifulSoup, Tag


ALLOWED_TAGS = [
    "p", "h1", "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li", "blockquote", "pre", "code",
    "strong", "em", "a", "img", "hr", "br", "table",
    "thead", "tbody", "tr", "th", "td", "div", "span",   
    "svg", "circle", "line", "path", "rect",
]

ALLOWED_ATTRIBUTES = {
        "h1": ["id"],
    "a": ["href", "title"],
    "img": ["src", "alt", "title", "width", "height"],
    "code": ["class"],
    "td": ["align"],
    "th": ["align"],
    "div": ["class"],
    "span": ["class"],
    "svg": ["xmlns", "width", "height", "viewBox", "fill", "stroke",
            "stroke-width", "stroke-linecap", "stroke-linejoin"],
    "circle": ["cx", "cy", "r"],
    "line": ["x1", "y1", "x2", "y2"],
}

INFO_ICON = '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
     viewBox="0 0 24 24" fill="none" stroke="currentColor"
     stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="10"/>
  <line x1="12" y1="16" x2="12" y2="12"/>
  <line x1="12" y1="8" x2="12.01" y2="8"/>
</svg>'''

def group_article_content(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    factory = BeautifulSoup("", "html.parser")

    for bq in soup.find_all("blockquote"):
        inner_p = bq.find("p")
        text = copy.deepcopy(inner_p) if inner_p else None

        header = factory.new_tag("div")
        header["class"] = "blockquote-header"

        icon = factory.new_tag("span")
        icon["class"] = "blockquote-icon"
        svg = BeautifulSoup(INFO_ICON, "html.parser").find("svg")
        if svg:
            icon.append(copy.deepcopy(svg))

        label = factory.new_tag("span")
        label["class"] = "blockquote-label"
        label.string = "[ Note ]"

        header.append(icon)
        header.append(label)

        content = factory.new_tag("div")
        content["class"] = "blockquote-content"
        if text:
            content.append(text)

        bq.clear()
        bq.append(header)
        bq.append(content)

    def new_div(cls):
        tag = factory.new_tag("div")
        tag["class"] = cls
        return tag

    def slugify(text: str) -> str:
        return text.lower().strip().replace(" ", "-").replace("/", "-")

    elements = [el for el in soup.contents if isinstance(el, Tag)]
    result = BeautifulSoup("", "html.parser")

    current_h1 = None  # ← add
    current_h2 = None
    current_h3 = None

    for el in elements:
        el = copy.deepcopy(el)

        if el.name == "h1":
            el["id"] = slugify(el.get_text(strip=True))  
            current_h1 = new_div("block-h1")
            current_h2 = None
            current_h3 = None
            current_h1.append(el)
            result.append(current_h1)

        elif el.name == "h2":
            current_h3 = None
            current_h2 = new_div("block-h2")
            current_h2.append(el)
            (current_h1 if current_h1 else result).append(current_h2)

        elif el.name == "h3":
            current_h3 = new_div("block-h3")
            current_h3.append(el)
            (current_h2 or current_h1 or result).append(current_h3)

        elif el.name == "hr":
            spacer = new_div("article-break")
            (current_h3 or current_h2 or current_h1 or result).append(spacer)

        else:
            (current_h3 or current_h2 or current_h1 or result).append(el)

    return str(result)


def render_markdown(val):
    if not val:
        return ""
    html = markdown.markdown(
            val,
            extensions=["fenced_code", "tables", "nl2br", "toc"]
    )
    html = group_article_content(html)
    return bleach.clean(html, tags=ALLOWED_TAGS , attributes=ALLOWED_ATTRIBUTES)

def format_date(val):
    if val is None:
        return ""
    return val.strftime("%d %b %y").upper()

def extract_headings(body: str) -> list[dict]:
    html = markdown.markdown(body)
    soup = BeautifulSoup(html, "html.parser")
    return [
        {
            "text": h1.get_text(strip=True),
            "id": h1.get_text(strip=True).lower().strip().replace(" ", "-").replace("/", "-")
        }
        for h1 in soup.find_all("h1")
    ]
