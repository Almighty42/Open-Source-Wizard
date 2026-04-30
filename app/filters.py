import os
import copy

import markdown
import bleach
from bs4 import BeautifulSoup, Tag

from pygments import highlight as pygments_highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter

PYGMENTS_FORMATTER = HtmlFormatter(nowrap=True, stripnl=False)

def load_svg(filename: str):
    svg_path = os.path.join(os.path.dirname(__file__), "static", "assets", "icons", filename)
    with open(svg_path, "r") as f:
        return f.read()

INFO_ICON = load_svg("blockquote_info.svg")
COPY_ICON = load_svg("copy_code.svg")

C_ICON = load_svg("languages/c.svg")
CPP_ICON = load_svg("languages/cpp.svg")
CSS_ICON = load_svg("languages/css.svg")
HTML_ICON = load_svg("languages/html.svg")
JS_ICON = load_svg("languages/js.svg")
JSON_ICON = load_svg("languages/json.svg")
NGINX_ICON = load_svg("languages/nginx.svg")
PYTHON_ICON = load_svg("languages/python.svg")
YAML_ICON = load_svg("languages/yaml.svg")

ALLOWED_TAGS = [
    "p", "h1", "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li", "blockquote", "pre", "code",
    "strong", "em", "a", "img", "hr", "br", "table",
    "thead", "tbody", "tr", "th", "td", "div", "span",   
    "svg", "circle", "line", "path", "rect",
    "button", "rect", "path",  "defs", "clipPath", "g",
    "linearGradient", "stop"
]

ALLOWED_ATTRIBUTES = {
        "h1": ["id"],
    "a": ["href", "title"],
    "img": ["src", "alt", "title", "width", "height"],
    "code": ["class"],
    "td": ["align"],
    "th": ["align"],
    "div": ["class", "role", "data-copy"],
    "span": ["class"],
    "svg": ["xmlns", "width", "height", "viewBox", "fill", "stroke",  "clip-path"
            "stroke-width", "stroke-linecap", "stroke-linejoin"],
    "g": ["clip-path"],
    "clipPath": ["id"],
    "circle": ["cx", "cy", "r"],
    "line": ["x1", "y1", "x2", "y2"],
    "button": ["class", "aria-label", "data-copy"],
    "rect": ["x", "y", "width", "height", "rx", "ry", "fill"],
    "path": ["d", "stroke", "stroke-width", "stroke-linecap", "stroke-linejoin",
             "fill", "fill-rule", "clip-rule"],
    "linearGradient": ["id", "x1", "y1", "x2", "y2", "gradientUnits"],
    "stop": ["offset", "stop-color", "stop-opacity"],
}

INFO_ICON = '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
     viewBox="0 0 24 24" fill="none" stroke="currentColor"
     stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="10"/>
  <line x1="12" y1="16" x2="12" y2="12"/>
  <line x1="12" y1="8" x2="12.01" y2="8"/>
</svg>'''

COPY_ICON = '''
<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
<rect width="20" height="20" fill="none"/>
<path d="M8.75008 1.66896C8.18754 1.67658 7.84983 1.70915 7.57676 1.84828C7.26316 2.00807 7.00819 2.26303 6.84841 2.57664C6.70927 2.84971 6.6767 3.18742 6.66908 3.74996M16.2501 1.66896C16.8127 1.67658 17.1503 1.70915 17.4234 1.84828C17.737 2.00807 17.992 2.26303 18.1517 2.57664C18.2909 2.84971 18.3235 3.18741 18.3311 3.74995M18.3311 11.25C18.3235 11.8125 18.2909 12.1502 18.1517 12.4233C17.992 12.7369 17.737 12.9919 17.4234 13.1516C17.1503 13.2908 16.8127 13.3234 16.2501 13.331M18.3334 6.66662V8.33328M11.6668 1.66663H13.3334M4.33341 18.3333H10.6667C11.6002 18.3333 12.0669 18.3333 12.4234 18.1516C12.737 17.9919 12.992 17.7369 13.1517 17.4233C13.3334 17.0668 13.3334 16.6 13.3334 15.6666V9.33329C13.3334 8.39988 13.3334 7.93316 13.1517 7.57664C12.992 7.26303 12.737 7.00807 12.4234 6.84828C12.0669 6.66663 11.6002 6.66663 10.6667 6.66663H4.33341C3.4 6.66663 2.93328 6.66663 2.57676 6.84828C2.26316 7.00807 2.00819 7.26303 1.84841 7.57664C1.66675 7.93316 1.66675 8.39988 1.66675 9.33329V15.6666C1.66675 16.6 1.66675 17.0668 1.84841 17.4233C2.00819 17.7369 2.26316 17.9919 2.57676 18.1516C2.93328 18.3333 3.39999 18.3333 4.33341 18.3333Z" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
'''

LANGUAGE_LABELS = {
    "python": "Python",
    "c": "C",
    "cpp": "C++",
    "bash": "Bash",
    "sh": "Bash",
    "yaml": "YAML",
    "json": "JSON",
    "html": "HTML",
    "css": "CSS",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "nginx": "Nginx",
}

LANGUAGE_ICONS = {
    "python":     load_svg("languages/python.svg"),
    "c":          load_svg("languages/c.svg"),
    "cpp":        load_svg("languages/cpp.svg"),
    "css":        load_svg("languages/css.svg"),
    "html":       load_svg("languages/html.svg"),
    "javascript": load_svg("languages/js.svg"),
    "js":         load_svg("languages/js.svg"),
    "json":       load_svg("languages/json.svg"),
    "nginx":      load_svg("languages/nginx.svg"),
    "yaml":       load_svg("languages/yaml.svg"),
    "bash":       load_svg("languages/bash.svg"),
    "sh":         load_svg("languages/bash.svg"),
}

# Helpers for group_article_content
def slugify(text: str) -> str:
        return text.lower().strip().replace(" ", "-").replace("/", "-")

def new_div(factory, cls: str) -> Tag:
    tag = factory.new_tag("div")
    tag["class"] = cls
    return tag

def transform_blockquotes(soup: BeautifulSoup, factory: BeautifulSoup):
    for bq in soup.find_all("blockquote"):
        inner_p = bq.find("p")
        text = copy.deepcopy(inner_p) if inner_p else None

        icon = factory.new_tag("span")
        icon["class"] = "blockquote-icon"
        svg = BeautifulSoup(INFO_ICON, "html.parser").find("svg")
        if svg:
            icon.append(copy.deepcopy(svg))

        label = factory.new_tag("span")
        label["class"] = "blockquote-label"
        label.string = "[ Note ]"

        header = factory.new_tag("div")
        header["class"] = "blockquote-header"
        header.append(icon)
        header.append(label)

        content = factory.new_tag("div")
        content["class"] = "blockquote-content"
        if text:
            content.append(text)

        bq.clear()
        bq.append(header)
        bq.append(content)

# def transform_code_block(soup: BeautifulSoup, factory: BeautifulSoup):
#     for pre in soup.find_all("pre"):
#         code = pre.find("code")
#
#         lang_key = ""
#         lang_label = ""
#         if code:
#             classes = code.get("class") or []
#             for cls in classes:
#                 if cls.startswith("language-"):
#                     lang_key = cls.replace("language-", "").lower()
#                     break
#
#         lang_label = LANGUAGE_LABELS.get(lang_key, lang_key.upper() if lang_key else "")
#
#         raw_code = code.get_text() if code else pre.get_text()
#         try:
#             lexer = get_lexer_by_name(lang_key) if lang_key else TextLexer()
#         except Exception:
#             lexer = TextLexer()
#
#         highlighted_html = pygments_highlight(raw_code, lexer, PYGMENTS_FORMATTER)
#
#         if code:
#             code.clear()
#             highlighted_soup = BeautifulSoup(highlighted_html, "html.parser")
#             for child in list(highlighted_soup.children):
#                 code.append(copy.deepcopy(child))
#
#         lang_icon = factory.new_tag("span")
#         lang_icon["class"] = "code-lang-icon"
#
#         icon_svg_str = LANGUAGE_ICONS.get(lang_key)
#         if icon_svg_str:
#             icon_svg = BeautifulSoup(icon_svg_str, "html.parser").find("svg")
#             if icon_svg:
#                 lang_icon.append(copy.deepcopy(icon_svg))
#         else:
#             lang_icon.string = "{ }"
#
#         lang_div = factory.new_tag("div")
#         lang_div["class"] = "code-lang"
#         lang_div.append(lang_icon)
#         # lang_div.append(lang_text)
#
#         copy_svg = BeautifulSoup(COPY_ICON, "html.parser").find("svg")
#
#         copy_text = factory.new_tag("p")
#         copy_text["class"] = "code-copy-text"
#         copy_text.string = "COPY"
#
#         copy_svg = BeautifulSoup(COPY_ICON, "html.parser").find("svg")
#         copy_icon = factory.new_tag("span")
#         copy_icon["class"] = "code-copy-icon"
#         if copy_svg:
#             copy_icon.append(copy.deepcopy(copy_svg))
#
#         copy_btn = factory.new_tag("div")
#         copy_btn["class"] = "code-copy-btn"
#         copy_btn["data-copy"] = ""
#         copy_btn["role"] = "button"
#         copy_btn["aria-label"] = "Copy code"
#         copy_btn.append(copy_icon)
#         copy_btn.append(copy_text)
#
#         actions = factory.new_tag("div")
#         actions["class"] = "code-actions"
#         actions.append(copy_btn)
#         actions.append(lang_div)
#
#         code_content = factory.new_tag("div")
#         code_content["class"] = "code-content"
#         # highlight_wrapper = pre.parent if pre.parent and "highlight" in (pre.parent.get("class") or []) else pre
#         # code_content.append(copy.deepcopy(highlight_wrapper))
#         highlight_div = factory.new_tag("div")
#         highlight_div["class"] = "highlight"
#         highlight_div.append(copy.deepcopy(pre))
#         code_content.append(highlight_div)
#
#         wrapper = factory.new_tag("div")
#         wrapper["class"] = "code-block"
#         wrapper.append(actions)
#         wrapper.append(code_content)
#
#         pre.replace_with(wrapper)

def transform_code_block(soup: BeautifulSoup, factory: BeautifulSoup):
    for pre in soup.find_all("pre"):
        code = pre.find("code")

        lang_key = ""
        if code:
            brs = code.find_all("br")
            for br in brs:
                br.replace_with("\n")
            classes = code.get("class") or []
            for cls in classes:
                if cls.startswith("language-"):
                    lang_key = cls.replace("language-", "").lower()
                    break

        lang_label = LANGUAGE_LABELS.get(lang_key, lang_key.upper() if lang_key else "")

        # raw_code = code.get_text(separator="\n") if code else pre.get_text(separator="\n")

        raw_code = code.decode_contents() if code else pre.decode_contents()
        if lang_key == "python":
            print("PYTHON RAW:", repr(raw_code[:300]))
        import html as html_module
        raw_code = html_module.unescape(raw_code)  # ← add this line
        try:
            lexer = get_lexer_by_name(lang_key, stripnl=False) if lang_key else TextLexer(stripnl=False)
        except Exception:
            lexer = TextLexer()

        highlighted_html = pygments_highlight(raw_code, lexer, PYGMENTS_FORMATTER)

        new_code = factory.new_tag("code")
        if lang_key:
            new_code["class"] = f"language-{lang_key}"
        # highlighted_soup = BeautifulSoup(highlighted_html, "html.parser")
        # for child in list(highlighted_soup.children):
        #     new_code.append(copy.deepcopy(child))
    
        # parsed = BeautifulSoup(f"<div>{highlighted_html}</div>", "html.parser")
        # wrapper_div = parsed.find("div")
        # for child in list(wrapper_div.children):
        #     new_code.append(copy.deepcopy(child))

        new_code.insert(0, BeautifulSoup(highlighted_html, "html.parser"))

        new_pre = factory.new_tag("pre")
        new_pre.append(new_code)

        # Icons
        lang_icon = factory.new_tag("span")
        lang_icon["class"] = "code-lang-icon"
        icon_svg_str = LANGUAGE_ICONS.get(lang_key)
        if icon_svg_str:
            icon_svg = BeautifulSoup(icon_svg_str, "html.parser").find("svg")
            if icon_svg:
                lang_icon.append(copy.deepcopy(icon_svg))
        else:
            lang_icon.string = "{ }"

        lang_div = factory.new_tag("div")
        lang_div["class"] = "code-lang"
        lang_div.append(lang_icon)

        copy_text = factory.new_tag("p")
        copy_text["class"] = "code-copy-text"
        copy_text.string = "COPY"

        copy_svg = BeautifulSoup(COPY_ICON, "html.parser").find("svg")
        copy_icon_span = factory.new_tag("span")
        copy_icon_span["class"] = "code-copy-icon"
        if copy_svg:
            copy_icon_span.append(copy.deepcopy(copy_svg))

        copy_btn = factory.new_tag("div")
        copy_btn["class"] = "code-copy-btn"
        copy_btn["data-copy"] = ""
        copy_btn["role"] = "button"
        copy_btn["aria-label"] = "Copy code"
        copy_btn.append(copy_icon_span)
        copy_btn.append(copy_text)

        actions = factory.new_tag("div")
        actions["class"] = "code-actions"
        actions.append(copy_btn)
        actions.append(lang_div)

        highlight_div = factory.new_tag("div")
        highlight_div["class"] = "highlight"
        highlight_div.append(new_pre)

        code_content = factory.new_tag("div")
        code_content["class"] = "code-content"
        code_content.append(highlight_div)

        wrapper = factory.new_tag("div")
        wrapper["class"] = "code-block"
        wrapper.append(actions)
        wrapper.append(code_content)

        pre.replace_with(wrapper)

def group_by_headings(elements: list[Tag], factory: BeautifulSoup) -> BeautifulSoup:
    result = BeautifulSoup("", "html.parser")
    current_h1 = current_h2 = current_h3 = None

    for el in elements:
        el = copy.deepcopy(el)

        if el.name == "h1":
            el["id"] = slugify(el.get_text(strip=True))
            current_h1 = new_div(factory, "block-h1")
            current_h2 = current_h3 = None
            current_h1.append(el)
            result.append(current_h1)

        elif el.name == "h2":
            current_h3 = None
            current_h2 = new_div(factory, "block-h2")
            current_h2.append(el)
            (current_h1 or result).append(current_h2)

        elif el.name == "h3":
            current_h3 = new_div(factory, "block-h3")
            current_h3.append(el)
            (current_h2 or current_h1 or result).append(current_h3)

        elif el.name == "hr":
            spacer = new_div(factory, "article-break")
            (current_h3 or current_h2 or current_h1 or result).append(spacer)

        else:
            (current_h3 or current_h2 or current_h1 or result).append(el)

    return result

def group_article_content(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    factory = BeautifulSoup("", "html.parser")

    transform_blockquotes(soup, factory)
    transform_code_block(soup, factory)

    elements = [el for el in soup.contents if isinstance(el, Tag)]
    result = group_by_headings(elements, factory)

    return str(result)

import re
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
    html = markdown.markdown(body)
    soup = BeautifulSoup(html, "html.parser")
    return [
        {
            "text": h1.get_text(strip=True),
            "id": h1.get_text(strip=True).lower().strip().replace(" ", "-").replace("/", "-")
        }
        for h1 in soup.find_all("h1")
    ]
