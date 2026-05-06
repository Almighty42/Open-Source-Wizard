import re
import os
from flask import url_for

VIDEO_EXTENSIONS = {".mp4", ".webm", ".ogg"}

def _norm_key(path: str) -> str:
    return path.lstrip("/")

def _norm_src(path: str) -> str:
    return "/" + _norm_key(path)

def resolve_asset_images(body: str, article_assets) -> str:
    asset_map = {}
    for aa in article_assets:
        k = _norm_key(aa.asset.path)
        asset_map[k] = aa.asset
        asset_map[str(aa.asset.id)] = aa.asset

    def replace(match):
        alt = match.group(1)
        key = match.group(2).strip()
        asset = asset_map.get(_norm_key(key)) or asset_map.get(key)
        if not asset:
            return ""

        src = _norm_src(asset.path)
        caption = asset.caption or ""
        ext = os.path.splitext(asset.path)[1].lower()

        if ext in VIDEO_EXTENSIONS:
            mime = {"mp4": "video/mp4", "webm": "video/webm", "ogg": "video/ogg"}[ext.lstrip(".")]
            return (
                f'<figure class="video-block">\n'
                f'<video controls preload="metadata">\n'
                f'<source src="{src}" type="{mime}">\n'
                f'</video>\n'
                f'{"<figcaption>" + caption + "</figcaption>" if caption else ""}\n'
                f'</figure>'
            )

        css_class = "diagram" if ext == ".svg" else "inline-image"
        return (
            f'<figure class="{css_class}">\n'
            f'<img src="{src}" alt="{alt or asset.alt_text or ""}" loading="lazy" />\n'
            f'{"<figcaption>" + caption + "</figcaption>" if caption else ""}\n'
            f'</figure>'
        )

    return re.sub(r'!\[([^\]]*)\]\(asset:([^\)]+)\)', replace, body)
