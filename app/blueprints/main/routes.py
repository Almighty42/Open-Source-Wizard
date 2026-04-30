from flask import  render_template
from . import main_bp
from app import db
from app.models import Article, Project
from app.models.base import Status

@main_bp.route("/")
@main_bp.route("/index")
def index():

    articles = db.session.query(Article) \
    .filter(Article.status == Status.published) \
    .order_by(Article.published_at.desc()) \
    .limit(3) \
    .all()

    projects = db.session.query(Project) \
    .filter(Project.status == Status.published) \
    .order_by(Project.published_at.desc()) \
    .limit(3) \
    .all()

    # TODO: Add links to article cards, for categories and tags
    # TODO: Add links to project cards, for categories and tags
    # TODO: Add a introductory text for new visitors

    return render_template("main/index.html", articles=articles, projects=projects)

@main_bp.route("/about")
def about():
    return render_template("main/about.html")
