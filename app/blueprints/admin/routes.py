from flask import  render_template, request, flash, abort, url_for, redirect
from app.filters.render import render_markdown
from app.forms import ArticleForm, TagForm, CategoryForm
from app.models import Article, ArticleAsset, ArticleCategory, ArticleTag
from app import db
from . import admin_bp
from .utils import ( 
                    fetch_categories,
                    fetch_assets,
                    fetch_tags,
                    add_article_db,
                    add_tag_db,
                    add_category_db,
                    update_article_db,
                    build_category_choices,
                    build_tag_choices,
                    build_cover_asset_choices,
                    build_attachment_asset_choices,
                    )

from app.decorators import admin_required

from sqlalchemy.orm import joinedload

@admin_bp.route("/add-article", methods=["GET", "POST"])
@admin_required
def add_article():
    # TODO: ERROR HANDLING
    # 1. Filter for attachments as there will be too many, or some other solution
    # 2. Sort order bug

    form = ArticleForm()

    categories = fetch_categories()
    tags = fetch_tags()
    assets = fetch_assets()

    # Populate form with data
    form.category.choices = build_category_choices(categories)
    form.tags.choices = build_tag_choices(tags)
    form.cover_asset.choices = build_cover_asset_choices(assets)
    form.attachment_assets.choices = build_attachment_asset_choices(assets)

    preview_html = None

    if request.method == "POST":
        if form.validate_on_submit():
            if form.preview.data:
                preview_html = render_markdown(form.body.data)

            elif form.submit.data:
                return add_article_db(form)
        else:
            flash("Please fix the errors in the form.", "error")

    return render_template(
        "admin/article-form.html",
        form=form,
        preview_html=preview_html,
        page_title="Add Article",
        submit_label="Add Article",
        form_action=url_for("admin.add_article"),
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
            cover_asset=next(
                (aa.asset_id for aa in article.article_assets if aa.role == "cover"),
                None,
            ),
            attachment_assets=[
                aa.asset_id for aa in article.article_assets if aa.role == "attachment"
            ],
            published_at=article.published_at.date() if article.published_at else None,
        )

    form.category.choices = build_category_choices(categories)
    form.tags.choices = build_tag_choices(tags)
    form.cover_asset.choices = build_cover_asset_choices(assets)
    form.attachment_assets.choices = build_attachment_asset_choices(assets)

    preview_html = None

    if form.validate_on_submit():
        if form.preview.data:
            preview_html = render_markdown(form.body.data)

        elif form.submit.data:
            return update_article_db(article, form)

    elif request.method == "POST":
        flash("Please fix the errors in the form.", "error")

    return render_template(
        "admin/article-form.html",
        form=form,
        preview_html=preview_html,
        page_title="Edit Article",
        submit_label="Update Article",
        form_action=url_for("admin.edit_article", slug=article.slug),
    )

@admin_bp.route("/delete-article/<slug>", methods=["POST"])
@admin_required
def delete_article(slug):
    article = db.session.query(Article).where(Article.slug == slug).first()

    if article is None:
        abort(404)

    try:
        db.session.delete(article)
        db.session.commit()
        flash(f'Article "{article.title}" deleted successfully.', "success")
    except Exception:
        db.session.rollback()
        flash("Failed to delete article.", "error")

    return redirect(url_for("article.articles"))

@admin_bp.route("/add-tag", methods=["GET", "POST"])
@admin_required
def add_tag():
    form = TagForm()

    if form.validate_on_submit():
        add_tag_db(form)
    elif form.is_submitted():
        flash("Please fix the errors in the form.", "error")

    return render_template("admin/add-tag.html", form=form)


@admin_bp.route("/add-category", methods=["GET", "POST"])
@admin_required
def add_category():
    form = CategoryForm()

    if form.validate_on_submit():
        add_category_db(form)
    elif form.is_submitted():
        flash("Please fix the errors in the form.", "error")

    return render_template("admin/add-category.html", form=form)
