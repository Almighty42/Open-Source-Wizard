from app.models import (
        Category,
        Tag,
        Asset,
        Article,
        ArticleTag,
        ArticleCategory,
        ArticleAsset
        )
from flask import redirect, url_for, flash
from app.utils import calculate_read_time
from app import db

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

def add_article_db(form_data):
    try:
        article = _build_article(form_data)
        selected_category = _get_selected_category(form_data)
        selected_tags = _get_selected_tags(form_data)
        cover_asset = _get_cover_asset(form_data)
        attachment_assets = _get_attachment_assets(form_data)

        db.session.add(article)
        db.session.flush()

        _add_article_category(article, selected_category)
        _add_article_tags(article, selected_tags)
        _add_article_assets(article, cover_asset, attachment_assets)

        db.session.commit()
        return redirect(url_for("article.article", slug=article.slug))

    except Exception:
        db.session.rollback()
        raise


def _build_article(form_data):
    return Article(
        title=form_data.title.data.strip(),
        slug=form_data.slug.data.strip(),
        body=form_data.body.data,
        status=form_data.status.data,
        published_at=form_data.published_at.data or None,
        excerpt=form_data.excerpt.data.strip(),
        read_time=calculate_read_time(form_data.body.data),
        author_id=current_user.id,
        seo_title=form_data.title.data.strip(),
        seo_description=form_data.excerpt.data.strip(),
    )


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


def _add_article_category(article, category):
    if not category:
        return

    article.article_categories.append(
        ArticleCategory(
            category_id=category.id,
            is_primary=True,
        )
    )


def _add_article_tags(article, tags):
    for index, tag in enumerate(tags):
        article.article_tags.append(
            ArticleTag(
                tag_id=tag.id,
                sort_order=index,
            )
        )


def _add_article_assets(article, cover_asset, attachment_assets):
    if cover_asset:
        article.article_assets.append(
            ArticleAsset(
                asset_id=cover_asset.id,
                role="cover",
            )
        )

    for index, asset in enumerate(attachment_assets, start=1):
        if cover_asset and asset.id == cover_asset.id:
            continue

        article.article_assets.append(
            ArticleAsset(
                asset_id=asset.id,
                role="attachment",
                sort_order=index,
            )
        )

def add_tag_db(form_data):
    try:
        tag = Tag(
            name=form_data.name.data.strip(),
            slug=form_data.slug.data.strip(),
            description=form_data.description.data.strip() if form_data.description.data else None,
            seo_title=form_data.seo_title.data.strip() if form_data.seo_title.data else None,
            seo_description=form_data.seo_description.data.strip() if form_data.seo_description.data else None,
        )

        db.session.add(tag)
        db.session.commit()

        flash("Tag created successfully.", "success")
        return redirect(url_for("admin.add_tag"))

    except Exception:
        db.session.rollback()
        flash("Failed to create tag.", "error")

def add_category_db(form_data):
    try:
        category = Category(
            name=form_data.name.data.strip(),
            slug=form_data.slug.data.strip(),
            description=form_data.description.data.strip() if form_data.description.data else None,
            seo_title=form_data.seo_title.data.strip() if form_data.seo_title.data else None,
            seo_description=form_data.seo_description.data.strip() if form_data.seo_description.data else None,
            sort_order=form_data.sort_order.data or 0,
        )

        db.session.add(category)
        db.session.commit()

        flash("Category created successfully.", "success")
        return redirect(url_for("admin.add_category"))

    except Exception:
        db.session.rollback()
        flash("Failed to create category.", "error")

def update_article_db(article, form_data):
    try:
        selected_category = _get_selected_category(form_data)
        selected_tags = _get_selected_tags(form_data)
        cover_asset = _get_cover_asset(form_data)
        attachment_assets = _get_attachment_assets(form_data)

        article.title = form_data.title.data.strip()
        article.slug = form_data.slug.data.strip()
        article.body = form_data.body.data
        article.status = form_data.status.data
        article.published_at = form_data.published_at.data or None
        article.excerpt = form_data.excerpt.data.strip()
        article.read_time = calculate_read_time(form_data.body.data)
        article.seo_title = form_data.title.data.strip()
        article.seo_description = form_data.excerpt.data.strip()

        article.article_categories.clear()
        article.article_tags.clear()
        article.article_assets.clear()

        _add_article_category(article, selected_category)
        _add_article_tags(article, selected_tags)
        _add_article_assets(article, cover_asset, attachment_assets)

        db.session.commit()
        flash("Article updated successfully.", "success")
        return redirect(url_for("article.article", slug=article.slug))

    except Exception:
        db.session.rollback()
        raise
