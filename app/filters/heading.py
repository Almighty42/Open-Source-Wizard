import copy
import re

from bs4 import BeautifulSoup, Tag


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s/-]", "", text)
    text = re.sub(r"[\s/]+", "-", text)
    return text.strip("-")


def make_block(factory: BeautifulSoup, class_name: str) -> Tag:
    tag = factory.new_tag("div")
    tag["class"] = class_name
    return tag


def group_by_headings(elements: list[Tag], factory: BeautifulSoup) -> BeautifulSoup:
    result = BeautifulSoup("", "html.parser")
    current_h1 = current_h2 = current_h3 = None

    for element in elements:
        element = copy.deepcopy(element)

        if element.name == "h1":
            element["id"] = slugify(element.get_text(strip=True))
            current_h1 = make_block(factory, "block-h1")
            current_h2 = current_h3 = None
            current_h1.append(element)
            result.append(current_h1)

        elif element.name == "h2":
            current_h3 = None
            current_h2 = make_block(factory, "block-h2")
            current_h2.append(element)
            (current_h1 or result).append(current_h2)

        elif element.name == "h3":
            current_h3 = make_block(factory, "block-h3")
            current_h3.append(element)
            (current_h2 or current_h1 or result).append(current_h3)

        elif element.name == "hr":
            spacer = make_block(factory, "article-break")
            (current_h3 or current_h2 or current_h1 or result).append(spacer)

        else:
            (current_h3 or current_h2 or current_h1 or result).append(element)

    return result
