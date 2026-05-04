import os
from markupsafe import Markup
from flask import current_app
from datetime import datetime, timezone
import math
import re

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def inline_svg(filename):
    path = os.path.join(current_app.static_folder, filename)
    with open(path) as f:
        return Markup(f.read())


def calculate_read_time(markdown_text: str, words_per_minute: int = 238) -> int:
    if not markdown_text:
        return 1

    text = markdown_text

    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"[*_~>#-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    word_count = len(re.findall(r"\b\w+\b", text))

    return max(1, math.ceil(word_count / words_per_minute))
