import re
import markdown
from markupsafe import Markup
from flask import url_for
from app.models import Asset
from app.extensions import db

def resolve_asset_images(body: str, article_assets) -> str:
    asset_map = {str(aa.asset.id): aa.asset for aa in article_assets}

    def replace(match):
        alt = match.group(1)
        asset_id = match.group(2)
        asset = asset_map.get(asset_id)
        if not asset:
            return ""
        src = url_for('static', filename=asset.path)
        caption = asset.caption or ""
        return f'<figure>\n<img src="{src}" alt="{alt or asset.alt_text or ""}" loading="lazy" />\n{"<figcaption>" + caption + "</figcaption>" if caption else ""}\n</figure>'

    return re.sub(r'!\[([^\]]*)\]\(asset:(\w+)\)', replace, body)
