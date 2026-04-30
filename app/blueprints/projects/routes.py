from flask import  render_template, abort
from app.models.project import ProjectAsset, Project
from . import project_bp
from app import db
from app.filters import extract_headings

from sqlalchemy.orm import joinedload

@project_bp.route("/")
def projects():
    return render_template("projects/projects.html")

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

    return render_template("projects/project.html", 
                           project=project,
                           cover=cover,
                           project_headings=project_headings,
                           tags=tags,
                           primary_category=primary_category
    )
