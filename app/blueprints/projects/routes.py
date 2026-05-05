from flask import  render_template, abort, request
from flask_login import current_user
from app.models import ProjectAsset, Project, Category, Tag
from app.models.base import Status, Role
from . import project_bp
from app import db
from app.filters import extract_headings
from app.forms import DeleteForm
from app.filters import render_markdown

from sqlalchemy.orm import joinedload

@project_bp.route("/")
def projects():
    # TODO: LATER - Implement date filtering at a later date...
    q         = request.args.get("q", "").strip()
    category  = request.args.get("category", "")
    tag_slugs = request.args.getlist("tag")
    page      = request.args.get("page", 1, type=int)
    per_page  = 5

    query = Project.query.options(
        joinedload(Project.project_assets).joinedload(ProjectAsset.asset)
    )

    if not (current_user.is_authenticated and current_user.is_admin):
        query = query.filter(
            Project.published_at.isnot(None),
            Project.status == Status.published,
        )

    if q:
        query = query.filter(Project.title.ilike(f"%{q}%"))

    if category:
        query = query.filter(Project.categories.any(Category.slug == category))

    if tag_slugs:
        for slug in tag_slugs:
            query = query.filter(Project.tags.any(Tag.slug == slug))

    pagination = query.order_by(Project.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    categories = Category.query.order_by(Category.name).all()
    tags = Tag.query.order_by(Tag.name).all()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render_template(
            "projects/_projects_list.html",
            projects=pagination.items,
            pagination=pagination,
        )

    return render_template(
        "projects/projects.html",
        projects=pagination.items,
        pagination=pagination,
        categories=categories,
        tags=tags,
        is_admin=current_user.is_authenticated,
        title="Projects",
    )

@project_bp.route("/<slug>")
def project(slug):
    project = (
            db.session.query(Project)
            .options(joinedload(Project.project_assets).joinedload(ProjectAsset.asset))
            .where(Project.slug == slug)
            .first()
    )

    if project is None:
        abort(404)

    project_headings = extract_headings(project.body)
    cover = next((aa.asset for aa in project.project_assets if aa.is_cover), None)
    tags = [at.tag for at in project.project_tags]
    primary_category = next((ac.category for ac in project.project_categories if ac.is_primary), None)
    attachments = [
        aa
        for aa in project.project_assets
        if aa.role == Role.attachment
    ]
    rendered_body = render_markdown(project.body, project.project_assets)
    delete_form = DeleteForm()

    return render_template("projects/project.html", 
                           project=project,
                           rendered_body=rendered_body,
                           cover=cover,
                           project_headings=project_headings,
                           tags=tags,
                           primary_category=primary_category,
                           attachments=attachments,
                           is_auth=current_user.is_authenticated,
                            delete_form=delete_form,
                            title="Project",
    )
