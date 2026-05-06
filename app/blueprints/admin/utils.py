# TODO: REFACTOR
from app.models import (
    Category,
    Tag,
    Asset,
)

def fetch_categories() -> list[Category]:
    return Category.query.order_by(Category.name).all()

def fetch_tags() -> list[Tag]:
    return Tag.query.order_by(Tag.name).all()

def fetch_assets() -> list[Asset]:
    return Asset.query.order_by(Asset.path).all()

def build_category_choices(categories):
    return [("", "Select category")] + [
        (category.slug, category.name) for category in categories
    ]

def build_tag_choices(tags):
    return [
        (tag.slug, tag.name) for tag in tags
    ]

def build_cover_asset_choices(assets):
    return [(None, "No cover")] + [
        (asset.id, asset.path) for asset in assets
    ]

def build_attachment_asset_choices(assets):
    return [
        (asset.id, asset.path) for asset in assets
    ]

def build_inline_asset_choices(assets):
    return [
        (asset.id, asset.path) for asset in assets
    ]

