from app import db
from app.models import Article
from app.utils import calculate_read_time
from app.blueprints.admin.exceptions import ArticleCreateError, ArticleDeleteError, ArticleUpdateError
from app.blueprints.admin.services.articles.articles_builders import (
        build_article, add_article_assets, add_article_category, add_article_tags
        )
from app.blueprints.admin.services.form_resolvers import ( 
        get_attachment_assets, get_cover_asset, get_inline_assets, get_selected_category, get_selected_tags
        )
from app.blueprints.admin.services.assets.asset_storage import delete_asset_if_unused

def create_article(form_data) -> Article:
    try:
        article = build_article(form_data)
        selected_category = get_selected_category(form_data)
        selected_tags = get_selected_tags(form_data)
        cover_asset = get_cover_asset(form_data)
        inline_assets = get_inline_assets(form_data)
        attachment_assets = get_attachment_assets(form_data)

        db.session.add(article)
        db.session.flush()

        add_article_category(article, selected_category)
        add_article_tags(article, selected_tags)
        add_article_assets(article, cover_asset, inline_assets, attachment_assets)

        db.session.commit()

        return article

    except Exception:
        db.session.rollback()
        raise ArticleCreateError()

def update_article(article, form_data) -> Article:
    try:
        selected_category = get_selected_category(form_data)
        selected_tags = get_selected_tags(form_data)
        cover_asset = get_cover_asset(form_data)
        inline_assets = get_inline_assets(form_data)
        attachment_assets = get_attachment_assets(form_data)

        article.title = form_data.title.data.strip()
        article.slug = form_data.slug.data.strip()
        article.body = form_data.body.data
        article.status = form_data.status.data
        article.published_at = form_data.published_at.data or None
        article.excerpt = form_data.excerpt.data.strip()
        article.is_featured = form_data.is_featured.data
        article.read_time = calculate_read_time(form_data.body.data)
        article.seo_title = form_data.title.data.strip()
        article.seo_description = form_data.excerpt.data.strip()

        article.article_categories.clear()
        article.article_tags.clear()
        article.article_assets.clear()

        add_article_category(article, selected_category)
        add_article_tags(article, selected_tags)
        add_article_assets(article, cover_asset, inline_assets, attachment_assets)

        db.session.commit()

        return article

    except Exception:
        db.session.rollback()
        raise ArticleUpdateError()

def remove_article(article) -> None:
    try:
        linked_assets = [aa.asset for aa in article.article_assets]

        db.session.delete(article)
        db.session.flush()

        for asset in linked_assets:
            delete_asset_if_unused(asset)

        db.session.commit()

    except Exception:
        db.session.rollback()
        raise ArticleDeleteError()

