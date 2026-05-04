import copy
import html as html_module

from bs4 import BeautifulSoup, Tag
from pygments import highlight as pygments_highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter

from .icons import COPY_ICON, LANGUAGE_ICONS

PYGMENTS_FORMATTER = HtmlFormatter(nowrap=True, stripnl=False)

def extract_language(code: Tag | None) -> str:
    if not code:
        return ""

    for br in code.find_all("br"):
        br.replace_with("\n")

    for cls in code.get("class") or []:
        if cls.startswith("language-"):
            return cls.replace("language-", "").lower()

    return ""

def extract_raw_code(pre: Tag, code: Tag | None) -> str:
    node = code if code else pre

    parts = []
    for child in node.children:
        if isinstance(child, str):
            parts.append(child)
        elif getattr(child, "name", None) == "br":
            parts.append("\n")
        else:
            parts.append(child.get_text())

    return html_module.unescape("".join(parts))

def highlight_code(raw_code: str, lang_key: str) -> str:
    try:
        lexer = get_lexer_by_name(lang_key, stripnl=False) if lang_key else TextLexer(stripnl=False)
    except Exception:
        lexer = TextLexer(stripnl=False)

    return pygments_highlight(raw_code, lexer, PYGMENTS_FORMATTER)

def build_language_icon(factory: BeautifulSoup, lang_key: str) -> Tag:
    lang_icon = factory.new_tag("span")
    lang_icon["class"] = "code-lang-icon"

    icon_svg_str = LANGUAGE_ICONS.get(lang_key)
    if icon_svg_str:
        icon_svg = BeautifulSoup(icon_svg_str, "html.parser").find("svg")
        if icon_svg:
            lang_icon.append(copy.deepcopy(icon_svg))
    else:
        lang_icon.string = "{ }"

    return lang_icon

def build_copy_button(factory: BeautifulSoup, raw_code: str) -> Tag:
    copy_text = factory.new_tag("p")
    copy_text["class"] = "code-copy-text"
    copy_text.string = "COPY"

    copy_icon_span = factory.new_tag("span")
    copy_icon_span["class"] = "code-copy-icon"

    copy_svg = BeautifulSoup(COPY_ICON, "html.parser").find("svg")
    if copy_svg:
        copy_icon_span.append(copy.deepcopy(copy_svg))

    cleaned_code = raw_code.replace("\u00A0", " ").replace("\xa0", " ")

    copy_btn = factory.new_tag("div")
    copy_btn["class"] = "code-copy-btn"
    copy_btn["data-copy"] = cleaned_code
    copy_btn["role"] = "button"
    copy_btn["aria-label"] = "Copy code"
    copy_btn.append(copy_icon_span)
    copy_btn.append(copy_text)

    return copy_btn

def build_code_actions(factory: BeautifulSoup, lang_key: str, raw_code: str) -> Tag:
    lang_div = factory.new_tag("div")
    lang_div["class"] = "code-lang"
    lang_div.append(build_language_icon(factory, lang_key))

    actions = factory.new_tag("div")
    actions["class"] = "code-actions"
    actions.append(build_copy_button(factory, raw_code))
    actions.append(lang_div)

    return actions

def build_highlight_block(factory: BeautifulSoup, highlighted_html: str, lang_key: str) -> Tag:
    new_code = factory.new_tag("code")
    if lang_key:
        new_code["class"] = f"language-{lang_key}"

    new_code.insert(0, BeautifulSoup(highlighted_html, "html.parser"))

    new_pre = factory.new_tag("pre")
    new_pre.append(new_code)

    highlight_div = factory.new_tag("div")
    highlight_div["class"] = "highlight"
    highlight_div.append(new_pre)

    code_content = factory.new_tag("div")
    code_content["class"] = "code-content"
    code_content.append(highlight_div)

    return code_content

def build_code_wrapper(factory: BeautifulSoup, highlighted_html: str, lang_key: str, raw_code: str) -> Tag:
    wrapper = factory.new_tag("div")
    wrapper["class"] = "code-block"
    wrapper.append(build_code_actions(factory, lang_key, raw_code))
    wrapper.append(build_highlight_block(factory, highlighted_html, lang_key))
    return wrapper

def transform_code_block(soup: BeautifulSoup, factory: BeautifulSoup) -> None:
    for pre in soup.find_all("pre"):
        code = pre.find("code")
        lang_key = extract_language(code)
        raw_code = extract_raw_code(pre, code)
        highlighted_html = highlight_code(raw_code, lang_key)
        wrapper = build_code_wrapper(factory, highlighted_html, lang_key, raw_code)
        pre.replace_with(wrapper)
