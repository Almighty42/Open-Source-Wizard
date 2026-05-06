# TODO: IMPORTANT - Make sure that assets are also deleted when deleting articles / projects
from flask import  render_template
from . import main_bp
from app import db
from app.models import Article, Project, ProjectAsset
from app.models.base import Status

from sqlalchemy.orm import joinedload

@main_bp.route("/")
@main_bp.route("/index")
def index():
    articles = (
        db.session.query(Article)
        .filter(Article.status == Status.published)
        .order_by(Article.is_featured.desc(), Article.published_at.desc())
        .limit(3)
        .all()
    )

    projects = (
        db.session.query(Project)
        .options(
            joinedload(Project.project_assets).joinedload(ProjectAsset.asset)
        )
        .filter(Project.status == Status.published)
        .order_by(Project.is_featured.desc(), Project.published_at.desc())
        .limit(3)
        .all()
    )

    return render_template("main/index.html", articles=articles, projects=projects)

@main_bp.route("/about")
def about():
    return render_template(
            "main/about.html",
            title="About"
            )
