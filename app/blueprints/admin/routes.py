from flask import  render_template, request, flash, abort, url_for, redirect
from app.filters.render import render_markdown
from app.forms import ArticleForm, TagForm, CategoryForm, ProjectForm, AssetForm
from app.models import (
        Article,
        ArticleAsset,
        ArticleCategory,
        ArticleTag,
        Project,
        ProjectAsset,
        ProjectCategory,
        ProjectTag
        )
from app.models.base import Role
from app import db
from . import admin_bp
from .utils import ( 
                    fetch_categories,
                    fetch_assets,
                    fetch_tags,
                    add_article_db,
                    add_project_db,
                    add_tag_db,
                    add_category_db,
                    add_asset_db,
                    update_article_db,
                    update_project_db,
                    build_category_choices,
                    build_tag_choices,
                    build_cover_asset_choices,
                    build_attachment_asset_choices,
                    build_inline_asset_choices,
                    delete_article_db,
                    delete_project_db,
                    )

from app.decorators import admin_required

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
        is_project=False,
        title="Add Article",
    )


@admin_bp.route("/add-project", methods=["GET", "POST"])
@admin_required
def add_project():
    form = ProjectForm()

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

    if request.method == "POST":
        if form.validate_on_submit():
            if form.preview.data:
                preview_html = render_markdown(form.body.data)

            elif form.submit.data:
                return add_project_db(form)
        else:
            flash("Please fix the errors in the form.", "error")

    return render_template(
        "admin/article-form.html",
        form=form,
        preview_html=preview_html,
        page_title="Add Project",
        submit_label="Add Project",
        form_action=url_for("admin.add_project"),
        is_project=True,
        title="Add Project",
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

    return delete_article_db(article)

@admin_bp.route("/add-tag", methods=["GET", "POST"])
@admin_required
def add_tag():
    form = TagForm()

    if form.validate_on_submit():
        add_tag_db(form)
    elif form.is_submitted():
        flash("Please fix the errors in the form.", "error")

    return render_template(
            "admin/add-tag.html", 
            form=form,
            title="Add Tag",
            )


@admin_bp.route("/add-asset", methods=["GET", "POST"])
@admin_required
def add_asset():
    form = AssetForm()

    if form.validate_on_submit():
        add_asset_db(form)
    elif form.is_submitted():
        flash("Please fix the errors in the form.", "error")

    return render_template(
            "admin/add-asset.html",
            form=form,
            title="Add Asset",
            )


@admin_bp.route("/add-category", methods=["GET", "POST"])
@admin_required
def add_category():
    form = CategoryForm()

    if form.validate_on_submit():
        add_category_db(form)
    elif form.is_submitted():
        flash("Please fix the errors in the form.", "error")

    return render_template(
            "admin/add-category.html",
            form=form,
            title="Add Category",
            )

@admin_bp.route("/edit-project/<slug>", methods=["GET", "POST"])
@admin_required
def edit_project(slug):
    project = (
        db.session.query(Project)
        .options(
            joinedload(Project.project_assets).joinedload(ProjectAsset.asset),
            joinedload(Project.project_categories).joinedload(ProjectCategory.category),
            joinedload(Project.project_tags).joinedload(ProjectTag.tag),
        )
        .where(Project.slug == slug)
        .first()
    )

    if project is None:
        abort(404)

    categories = fetch_categories()
    tags = fetch_tags()
    assets = fetch_assets()

    if request.method == "POST":
        form = ProjectForm(original_project=project)
    else:
        form = ProjectForm(
            original_project=project,
            title=project.title,
            slug=project.slug,
            status=project.status.value if hasattr(project.status, "value") else project.status,
            project_state=project.project_state.value if hasattr(project.project_state, "value") else project.project_state,
            platform=project.platform,
            repo_url=project.repo_url,
            demo_url=project.demo_url,
            is_featured=project.is_featured,
            excerpt=project.excerpt,
            body=project.body,
            category=project.primary_category.slug if project.primary_category else "",
            tags=[tag.slug for tag in project.tags],
            cover_asset=next(
                (pa.asset_id for pa in project.project_assets if pa.is_cover or pa.role == Role.cover),
                None,
            ),
            inline_assets=[
                pa.asset_id for pa in project.project_assets if pa.role == Role.inline
            ],
            attachment_assets=[
                pa.asset_id for pa in project.project_assets if pa.role == Role.attachment
            ],
            published_at=project.published_at.date() if project.published_at else None,
            started_at=project.started_at.date() if project.started_at else None,
            completed_at=project.completed_at.date() if project.completed_at else None,
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
            return update_project_db(project, form)

    elif request.method == "POST":
        flash("Please fix the errors in the form.", "error")

    return render_template(
        "admin/article-form.html",
        form=form,
        preview_html=preview_html,
        page_title="Edit Project",
        submit_label="Update Project",
        form_action=url_for("admin.edit_project", slug=project.slug),
        is_project=True,
        title="Edit Project",
    )

@admin_bp.route("/delete-project/<slug>", methods=["POST"])
@admin_required
def delete_project(slug):
    project = (
        db.session.query(Project)
        .options(joinedload(Project.project_assets).joinedload(ProjectAsset.asset))
        .where(Project.slug == slug)
        .first()
    )

    if project is None:
        abort(404)

    return delete_project_db(project)
