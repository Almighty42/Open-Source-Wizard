from flask import render_template, request
from app.models import Category, Tag, Article
from app.extensions import limiter
from . import article_bp

@article_bp.route("/")
@limiter.limit("1/second", override_defaults=False)
def articles():
    category = request.args.get("category")
    tag = request.args.get("tag")

    query = Article.query

    if category:
        query = query.join(Category).filter(Category.slug == category)

    if tag:
        query = query.join(Tag).filter(tag.slug == tag)

    articles = query.order_by(Article.created_at.desc()).all()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render_template("partials/_articles_list.html", articles=articles)

    return render_template("articles/articles.html",
        articles=articles,
        categories=Category.query.all(),
        tags=Tag.query.all(),
    )
