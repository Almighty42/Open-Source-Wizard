from flask import abort, render_template
from flask_login import current_user
from app.models import  Article
from app import db
from app.models import ArticleAsset
from app.models.base import  Status
from . import article_bp
from app.filters import extract_headings

from sqlalchemy.orm import joinedload

@article_bp.route("/")
def articles():
    # category = request.args.get("category")
    # tag = request.args.get("tag")
    #
    # query = Article.query
    #
    # if category:
    #     query = query.join(Category).filter(Category.slug == category)
    #
    # if tag:
    #     query = query.join(Tag).filter(tag.slug == tag)
    #
    # articles = query.order_by(Article.created_at.desc()).all()
    #
    # if request.headers.get("X-Requested-With") == "XMLHttpRequest":
    #     return render_template("partials/_articles_list.html", articles=articles)

    return render_template("articles/articles.html",
        # articles=articles,
        # categories=Category.query.all(),
        # tags=Tag.query.all(),
    )

@article_bp.route("/<slug>")
def article(slug):
    # TODO: Setup icons for dark mode ( programming languages )
    # TODO: Back to the top of the page button
    # TODO: Edit article button
    # TODO: Images inside of article
    # TODO: Fix python code indentation
    # TODO: Add article footer info and tags
    # TODO: Look into if you need to set anything else up
    article = (
            db.session.query(Article)
            .options(joinedload(Article.article_assets).joinedload(ArticleAsset.asset))
            .where(Article.slug == slug)
            .first()
    )

    if article is None:
        abort(404)

    if (article.status == Status.draft or article.status == Status.archived) and \
        not (current_user.is_authenticated and current_user.is_admin):
        abort(404)

    article_headings = extract_headings(article.body)
    cover = next((aa.asset for aa in article.article_assets if aa.is_cover), None)
    tags = [at.tag for at in article.article_tags]
    primary_category = next((ac.category for ac in article.article_categories if ac.is_primary), None)

    return render_template("articles/article.html", 
                           article=article,
                           cover=cover,
                           article_headings=article_headings,
                           tags=tags,
                           primary_category=primary_category
    )
