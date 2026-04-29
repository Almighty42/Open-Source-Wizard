from flask import abort, render_template
from app.models import  Article
from app.extensions import limiter
from app import db
from app.models.article import ArticleAsset, ArticleCategory
from . import article_bp
from app.filters import extract_headings

from sqlalchemy.orm import joinedload

@article_bp.route("/")
@limiter.limit("1/second", override_defaults=False)
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
@limiter.limit("1/second", override_defaults=False)
def article(slug):
    article = (
            db.session.query(Article)
            .options(joinedload(Article.article_assets).joinedload(ArticleAsset.asset))
            .where(Article.slug == slug)
            .first()
    )

    article_headings = extract_headings(article.body)

    if article is None:
        abort(404)

    cover = next((aa.asset for aa in article.article_assets if aa.is_cover), None)

    return render_template("articles/article.html", 
                           article=article,
                           cover=cover,
                           article_headings=article_headings
    )
