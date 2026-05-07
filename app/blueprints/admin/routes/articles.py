from flask import  render_template, request, flash, abort, url_for, redirect
from app import db
from app.forms import ArticleForm
from app.filters.render import render_markdown
from app.models import (
        Article,
        ArticleAsset,
        ArticleCategory,
        ArticleTag,
        Role
        )
from app.decorators import admin_required
from app.blueprints.admin import admin_bp
from app.blueprints.admin.services import create_article, update_article, remove_article
from app.blueprints.admin.utils import (
        build_category_choices, build_attachment_asset_choices, build_cover_asset_choices, build_inline_asset_choices, build_tag_choices
        )
from app.blueprints.admin.exceptions import ArticleCreateError, ArticleUpdateError, ArticleDeleteError
from app.blueprints.admin.selectors import fetch_categories, fetch_tags, fetch_assets

from sqlalchemy.orm import joinedload

@admin_bp.route("/add-article", methods=["GET", "POST"])
@admin_required
def add_article():
    # TODO: LATER - Add sorting in the future...

    form = ArticleForm()

    categories = fetch_categories()
    tags = fetch_tags()
    assets = fetch_assets()

    # Populate form with data
    form.category.choices = build_category_choices(categories)
    form.tags.choices = build_tag_choices(tags)
    form.cover_asset.choices = build_cover_asset_choices(assets)
    form.inline_assets.choices = build_inline_asset_choices(assets)
    form.attachment_assets.choices = build_attachment_asset_choices(assets)

    preview_html = None

    if form.validate_on_submit():
        if form.preview.data:
            preview_html = render_markdown(form.body.data)

        elif form.submit.data:
            try:
                article = create_article(form)
                return redirect(url_for("article.article", slug=article.slug))
            except ArticleCreateError as e:
                # TODO: LOGGING
                flash(f"{e.message}")
    elif request.method == "POST":
        flash("Please fix the errors in the form.", "error")

    return render_template(
        "admin/article-form.html",
        form=form,
        preview_html=preview_html,
        page_title="Add Article",
        submit_label="Add Article",
        form_action=url_for("admin.add_article"),
        is_project=False,
        title="Add Article",
    )

@admin_bp.route("/edit-article/<slug>", methods=["GET", "POST"])
@admin_required
def edit_article(slug):
    article = (
        db.session.query(Article)
        .options(
            joinedload(Article.article_assets).joinedload(ArticleAsset.asset),
            joinedload(Article.article_categories).joinedload(ArticleCategory.category),
            joinedload(Article.article_tags).joinedload(ArticleTag.tag),
        )
        .where(Article.slug == slug)
        .first()
    )

    if article is None:
        abort(404)

    categories = fetch_categories()
    tags = fetch_tags()
    assets = fetch_assets()

    if request.method == "POST":
        form = ArticleForm(original_article=article)
    else:
        form = ArticleForm(
            original_article=article,
            title=article.title,
            slug=article.slug,
            status=article.status.value if hasattr(article.status, "value") else article.status,
            excerpt=article.excerpt,
            body=article.body,
            category=article.primary_category.slug if article.primary_category else "",
            tags=[tag.slug for tag in article.tags],
            is_featured=article.is_featured,
            cover_asset=next(
                (aa.asset_id for aa in article.article_assets if aa.role == Role.cover),
                None,
            ),
            inline_assets=[
                aa.asset_id for aa in article.article_assets if aa.role == Role.inline
            ],
            attachment_assets=[
                aa.asset_id for aa in article.article_assets if aa.role == Role.attachment
            ],
            published_at=article.published_at.date() if article.published_at else None,
        )

    form.category.choices = build_category_choices(categories)
    form.tags.choices = build_tag_choices(tags)
    form.cover_asset.choices = build_cover_asset_choices(assets)
    form.attachment_assets.choices = build_attachment_asset_choices(assets)
    form.inline_assets.choices = build_inline_asset_choices(assets)

    preview_html = None

    if form.validate_on_submit():
        if form.preview.data:
            preview_html = render_markdown(form.body.data)

        elif form.submit.data:
            try:
                updated_article = update_article(article, form)
                return redirect(url_for("article.article", slug=updated_article.slug))
            except ArticleUpdateError as e:
                # TODO: LOGGING
                flash(f"{e.message}")
    elif request.method == "POST":
        flash("Please fix the errors in the form.", "error")

    return render_template(
        "admin/article-form.html",
        form=form,
        preview_html=preview_html,
        page_title="Edit Article",
        submit_label="Update Article",
        form_action=url_for("admin.edit_article", slug=article.slug),
        is_project=False,
        title="Edit Article",
    )

@admin_bp.route("/delete-article/<slug>", methods=["POST"])
@admin_required
def delete_article(slug):
    article = (
        db.session.query(Article)
        .options(joinedload(Article.article_assets).joinedload(ArticleAsset.asset))
        .where(Article.slug == slug)
        .first()
    )

    if article is None:
        abort(404)

    try:
        remove_article(article)
        flash(f'Article "{article.title}" deleted successfully.', "success")
        return redirect(url_for("article.articles"))
    except ArticleDeleteError as e:
        flash(f"{e.message}")
