import copy
import re

from bs4 import BeautifulSoup, Tag

HEADING_SHIFT = {"h1": "h2", "h2": "h3", "h3": "h4", "h4": "h5", "h5": "h6", "h6": "h6"}
HEADING_RE = re.compile(r"^h[1-6]$")
ANCHORED = {"h2", "h3", "h4"}


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s/-]", "", text)
    text = re.sub(r"[\s/]+", "-", text)
    return text.strip("-") or "section"


def make_block(factory: BeautifulSoup, class_name: str) -> Tag:
    tag = factory.new_tag("div")
    tag["class"] = class_name
    return tag


def shift_headings(soup: BeautifulSoup) -> None:
    # find_all returns a list first, so renaming in the loop can't double-shift
    for tag in soup.find_all(HEADING_RE):
        tag.name = HEADING_SHIFT[tag.name]


def top_level_tags(soup: BeautifulSoup) -> list[Tag]:
    return [el for el in soup.contents if isinstance(el, Tag)]


def assign_heading_ids(elements: list[Tag]) -> None:
    seen: dict[str, int] = {}
    for el in elements:
        if el.name in ANCHORED:
            base = slugify(el.get_text(strip=True))
            seen[base] = seen.get(base, 0) + 1
            el["id"] = base if seen[base] == 1 else f"{base}-{seen[base]}"


def collect_outline(elements: list[Tag]) -> list[dict]:
    outline: list[dict] = []
    for el in elements:
        if el.name not in ("h2", "h3"):
            continue
        item = {"text": el.get_text(strip=True), "id": el["id"], "children": []}
        if el.name == "h3" and outline:
            outline[-1]["children"].append(item)
        else:
            outline.append(item)  # h2, or an h3 with no h2 before it
    return outline


def group_by_headings(elements: list[Tag], factory: BeautifulSoup) -> BeautifulSoup:
    result = BeautifulSoup("", "html.parser")
    h2 = h3 = h4 = None

    for element in elements:
        element = copy.deepcopy(element)

        if element.name == "h2":
            h2 = make_block(factory, "block-h2")
            h3 = h4 = None
            h2.append(element)
            result.append(h2)

        elif element.name == "h3":
            h4 = None
            h3 = make_block(factory, "block-h3")
            h3.append(element)
            (h2 or result).append(h3)

        elif element.name == "h4":
            h4 = make_block(factory, "block-h4")
            h4.append(element)
            (h3 or h2 or result).append(h4)

        elif element.name == "hr":
            (h4 or h3 or h2 or result).append(make_block(factory, "article-break"))

        else:
            (h4 or h3 or h2 or result).append(element)

    return result
