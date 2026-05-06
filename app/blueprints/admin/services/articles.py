from app import db
from app.blueprints.admin.exceptions import ArticleCreateError, ArticleDeleteError, ArticleUpdateError
import common
from app.models import Article, ArticleTag, ArticleAsset, ArticleCategory
from app.utils import calculate_read_time

# NOTE: Main functions
def create_article(form_data) -> Article:
    try:
        article = _build_article(form_data)
        selected_category = common._get_selected_category(form_data)
        selected_tags = common._get_selected_tags(form_data)
        cover_asset = common._get_cover_asset(form_data)
        inline_assets = common._get_inline_assets(form_data)
        attachment_assets = common._get_attachment_assets(form_data)

        db.session.add(article)
        db.session.flush()

        _add_article_category(article, selected_category)
        _add_article_tags(article, selected_tags)
        _add_article_assets(article, cover_asset, inline_assets, attachment_assets)

        db.session.commit()

        return article

    except Exception:
        db.session.rollback()
        raise ArticleCreateError()

def update_article(article, form_data) -> Article:
    try:
        selected_category = common._get_selected_category(form_data)
        selected_tags = common._get_selected_tags(form_data)
        cover_asset = common._get_cover_asset(form_data)
        inline_assets = common._get_inline_assets(form_data)
        attachment_assets = common._get_attachment_assets(form_data)

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

        _add_article_category(article, selected_category)
        _add_article_tags(article, selected_tags)
        _add_article_assets(article, cover_asset, inline_assets, attachment_assets)

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
            common._delete_asset_if_unused(asset)

        db.session.commit()

    except Exception:
        db.session.rollback()
        raise ArticleDeleteError()

# NOTE: Helper Functions
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

def _add_article_tags(article, tags):
    for index, tag in enumerate(tags):
        article.article_tags.append(
            ArticleTag(
                tag_id=tag.id,
                sort_order=index,
            )
        )

def _add_article_assets(article, cover_asset, inline_assets, attachment_assets):
    used_asset_ids = set()

    if cover_asset:
        article.article_assets.append(
            ArticleAsset(
                asset_id=cover_asset.id,
                role="cover",
                is_cover=True,
            )
        )
        used_asset_ids.add(cover_asset.id)

    for asset in inline_assets:
        if asset.id in used_asset_ids:
            continue

        article.article_assets.append(
            ArticleAsset(
                asset_id=asset.id,
                role="inline",
                is_cover=False,
            )
        )
        used_asset_ids.add(asset.id)

    for asset in attachment_assets:
        if asset.id in used_asset_ids:
            continue

        article.article_assets.append(
            ArticleAsset(
                asset_id=asset.id,
                role="attachment",
                is_cover=False,
            )
        )
        used_asset_ids.add(asset.id)

def _add_article_category(article, category):
    if not category:
        return

    article.article_categories.append(
        ArticleCategory(
            category_id=category.id,
            is_primary=True,
        )
    )
