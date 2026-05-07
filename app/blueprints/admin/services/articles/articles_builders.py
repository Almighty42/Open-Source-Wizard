from app.models import Article, ArticleTag, ArticleAsset, ArticleCategory
from app.utils import calculate_read_time
from flask_login import current_user

def build_article(form_data):
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

def add_article_tags(article, tags):
    for index, tag in enumerate(tags):
        article.article_tags.append(
            ArticleTag(
                tag_id=tag.id,
                sort_order=index,
            )
        )

def add_article_assets(article, cover_asset, inline_assets, attachment_assets):
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

def add_article_category(article, category):
    if not category:
        return

    article.article_categories.append(
        ArticleCategory(
            category_id=category.id,
            is_primary=True,
        )
    )
