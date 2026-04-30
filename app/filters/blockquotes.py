import copy
from bs4 import BeautifulSoup

from .icons import INFO_ICON


def transform_blockquotes(soup: BeautifulSoup, factory: BeautifulSoup) -> None:
    info_svg = BeautifulSoup(INFO_ICON, "html.parser").find("svg")

    for blockquote in soup.find_all("blockquote"):
        inner_paragraph = blockquote.find("p")
        text = copy.deepcopy(inner_paragraph) if inner_paragraph else None

        icon = factory.new_tag("span", attrs={"class": "blockquote-icon"})
        if info_svg:
            icon.append(copy.deepcopy(info_svg))

        label = factory.new_tag("span", attrs={"class": "blockquote-label"})
        label.string = "[ Note ]"

        header = factory.new_tag("div", attrs={"class": "blockquote-header"})
        header.append(icon)
        header.append(label)

        content = factory.new_tag("div", attrs={"class": "blockquote-content"})
        if text:
            content.append(text)

        blockquote.clear()
        blockquote.append(header)
        blockquote.append(content)
