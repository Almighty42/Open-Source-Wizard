import os
from models import Category, Tag, Asset, ProjectAsset, ArticleAsset
from app import db

def _get_selected_category(form_data):
    if not form_data.category.data:
        return None

    return Category.query.filter_by(slug=form_data.category.data).first()

def _get_selected_tags(form_data):
    if not form_data.tags.data:
        return []

    return Tag.query.filter(Tag.slug.in_(form_data.tags.data)).all()


def _get_cover_asset(form_data):
    if not form_data.cover_asset.data:
        return None

    return db.session.get(Asset, form_data.cover_asset.data)


def _get_attachment_assets(form_data):
    if not form_data.attachment_assets.data:
        return []

    return Asset.query.filter(
        Asset.id.in_(form_data.attachment_assets.data)
    ).all()

def _get_inline_assets(form_data):
    if not form_data.inline_assets.data:
        return []

    return Asset.query.filter(
        Asset.id.in_(form_data.inline_assets.data)
    ).all()


def _db_asset_path_to_filesystem(db_path: str):
    if not db_path:
        return None

    cleaned = db_path.lstrip("/")
    if not cleaned.startswith("static/"):
        return None

    return os.path.join("app", cleaned)

def _delete_asset_file(db_path: str):
    absolute_path = _db_asset_path_to_filesystem(db_path)

    if absolute_path and os.path.exists(absolute_path):
        os.remove(absolute_path)

def _asset_is_still_used(asset_id: int) -> bool:
    article_use = db.session.query(ArticleAsset).filter_by(asset_id=asset_id).first()
    if article_use:
        return True

    project_use = db.session.query(ProjectAsset).filter_by(asset_id=asset_id).first()
    if project_use:
        return True

    return False

def _delete_asset_if_unused(asset: Asset):
    if asset is None:
        return

    if _asset_is_still_used(asset.id):
        return

    _delete_asset_file(asset.path)
    db.session.delete(asset)
