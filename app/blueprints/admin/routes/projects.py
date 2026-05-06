from flask import  render_template, request, flash, abort, url_for, redirect
from app import db
from app.forms import ProjectForm
from app.filters.render import render_markdown
from app.models import (
        Project,
        ProjectAsset,
        ProjectCategory,
        ProjectTag
        )
from app.decorators import admin_required
from app.blueprints.admin import admin_bp
from app.blueprints.admin.services import create_project, update_project, delete_project
from app.blueprints.admin.exceptions import ProjectCreateError, ProjectUpdateError, ProjectDeleteError

from sqlalchemy.orm import joinedload

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

    if form.validate_on_submit():
        if form.preview.data:
            preview_html = render_markdown(form.body.data)

        elif form.submit.data:
            try:
                project = create_project(form)
                return redirect(url_for("project.project", slug=project.slug))
            except ProjectCreateError as e:
                # TODO: LOGGING
                flash(f"{e.message}")
    elif request.method == "POST":
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
            try:
                updated_project = update_project(project, form)
                return redirect(url_for("project.project", slug=updated_project.slug))
            except ProjectUpdateError as e:
                # TODO: LOGGING
                flash(f"{e.message}")
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

    try:
        delete_project(project)
        flash(f'Project "{project.title}" deleted successfully.', "success")
        return redirect(url_for("project.projects"))
    except ProjectDeleteError as e:
        flash(f"{e.message}")
