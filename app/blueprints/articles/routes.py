from flask import abort, render_template, request
from flask_login import current_user
from app.filters import render_markdown
from app.models import  Article
from app import db
from app.models import (
        ArticleAsset,
        ArticleTag,
        ArticleCategory,
        Category,
        Tag,
        )
from app.models.base import  Status, Role
from . import article_bp
from app.filters import extract_headings
from app.forms import DeleteForm

from sqlalchemy.orm import joinedload

@article_bp.route("/")
def articles():
    # TODO: LATER - Implement date filtering at a later date...
    q         = request.args.get("q", "").strip()
    category  = request.args.get("category", "")
    tag_slugs = request.args.getlist("tag")
    page      = request.args.get("page", 1, type=int)
    per_page  = 5

    query = Article.query

    if not (current_user.is_authenticated and current_user.is_admin):
        query = query.filter(
            Article.published_at.isnot(None),
            Article.status == Status.published,
        )

    if q:
        query = query.filter(Article.title.ilike(f"%{q}%"))

    if category:
        query = query.filter(Article.categories.any(Category.slug == category))

    if tag_slugs:
        for slug in tag_slugs:
            query = query.filter(Article.tags.any(Tag.slug == slug))

    pagination = query.order_by(Article.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    categories = Category.query.order_by(Category.name).all()
    tags = Tag.query.order_by(Tag.name).all()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render_template(
            "articles/_articles_list.html",
            articles=pagination.items,
            pagination=pagination,
        )

    return render_template(
        "articles/articles.html",
        articles=pagination.items,
        pagination=pagination,
        categories=categories,
        tags=tags,
        is_admin=current_user.is_authenticated,
        title="Articles",
        description="Technical articles on embedded systems, electronics, and DIY hardware."
    )

@article_bp.route("/<slug>")
def article(slug):
    article = (
        db.session.query(Article)
        .options(
            joinedload(Article.article_assets).joinedload(ArticleAsset.asset),
            joinedload(Article.article_tags).joinedload(ArticleTag.tag),
            joinedload(Article.article_categories).joinedload(ArticleCategory.category),
        )
        .where(Article.slug == slug)
        .first()
    )

    if article is None:
        abort(404)

    if (
        article.status in (Status.draft, Status.archived)
        and not (current_user.is_authenticated and current_user.is_admin)
    ):
        abort(404)

    article_headings = extract_headings(article.body)
    cover = next(
        (aa.asset for aa in article.article_assets if aa.role == Role.cover),
        None,
    )
    tags = [at.tag for at in article.article_tags]
    primary_category = next(
        (ac.category for ac in article.article_categories if ac.is_primary),
        None,
    )
    attachments = [
        aa
        for aa in article.article_assets
        if aa.role == Role.attachment
    ]
    rendered_body = render_markdown(article.body, article.article_assets)
    delete_form = DeleteForm()

    return render_template(
        "articles/article.html",
        article=article,
        rendered_body=rendered_body,
        cover=cover,
        article_headings=article_headings,
        tags=tags,
        primary_category=primary_category,
        attachments=attachments,
        is_auth=current_user.is_authenticated,
        delete_form=delete_form,
        title=article.title, 
        description=article.excerpt
    )
