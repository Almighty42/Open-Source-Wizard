from app.models import Category, Tag, Asset
from app import db

def get_selected_category(form_data):
    if not form_data.category.data:
        return None

    return Category.query.filter_by(slug=form_data.category.data).first()

def get_selected_tags(form_data):
    if not form_data.tags.data:
        return []

    return Tag.query.filter(Tag.slug.in_(form_data.tags.data)).all()


def get_cover_asset(form_data):
    if not form_data.cover_asset.data:
        return None

    return db.session.get(Asset, form_data.cover_asset.data)


def get_attachment_assets(form_data):
    if not form_data.attachment_assets.data:
        return []

    return Asset.query.filter(
        Asset.id.in_(form_data.attachment_assets.data)
    ).all()

def get_inline_assets(form_data):
    if not form_data.inline_assets.data:
        return []

    return Asset.query.filter(
        Asset.id.in_(form_data.inline_assets.data)
    ).all()



