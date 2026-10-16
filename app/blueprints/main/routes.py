# TODO: LATER - Make a script to delete empty article / project folders
from flask import  current_app, make_response, render_template, url_for
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

    return render_template("main/index.html",
                           articles=articles,
                           projects=projects,
                            title="Home",
                            description="Electronics, embedded systems and DIY hardware.",
                            og_image=url_for('static', filename='assets/images/hero.svg', _external=True),
                           )

@main_bp.route("/about")
def about():
    return render_template(
            "main/about.html",
            title="About",
            description="Almighty42 — embedded systems developer and electronics enthusiast.",
            )

def _last_modified(item):
    value = item.updated_at or item.published_at

    if value is None:
        return None

    return value.date().isoformat()

@main_bp.get("/sitemap.xml")
def sitemap_xml():
    site_url = current_app.config["SITE_URL"]

    pages = [
        {
            "loc": site_url + url_for("main.index"),
            "lastmod": None,
        },
        {
            "loc": site_url + url_for("article.articles"),
            "lastmod": None,
        },
        {
            "loc": site_url + url_for("project.projects"),
            "lastmod": None,
        },
        {
            "loc": site_url + url_for("main.about"),
            "lastmod": None,
        },
    ]

    articles = (
        Article.query
        .filter(Article.status == Status.published)
        .order_by(Article.published_at.desc())
        .all()
    )

    for article in articles:
        pages.append({
            "loc": site_url + url_for(
                "article.article",
                slug=article.slug,
            ),
            "lastmod": _last_modified(article),
        })

    projects = (
        Project.query
        .filter(Project.status == Status.published)
        .order_by(Project.published_at.desc())
        .all()
    )

    for project in projects:
        pages.append({
            "loc": site_url + url_for(
                "project.project",
                slug=project.slug,
            ),
            "lastmod": _last_modified(project),
        })

    response = make_response(
        render_template("seo/sitemap.xml", pages=pages)
    )
    response.mimetype = "application/xml"
    response.headers["Cache-Control"] = "public, max-age=3600"

    return response

@main_bp.get("/robots.txt")
def robots_txt():
    response = make_response(
        render_template(
            "seo/robots.txt",
            site_url=current_app.config["SITE_URL"],
        )
    )
    response.mimetype = "text/plain"
    response.headers["Cache-Control"] = "public, max-age=86400"

    return response
