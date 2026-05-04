import os
from markupsafe import Markup
from flask import current_app
from datetime import datetime, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def inline_svg(filename):
    path = os.path.join(current_app.static_folder, filename)
    with open(path) as f:
        return Markup(f.read())
