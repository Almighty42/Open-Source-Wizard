from flask import   request
from flask_login import login_required
from app.decorators import admin_required
from . import api_bp
from app.models import Tag, Asset
from app import db

@api_bp.get("/tags")
@login_required
@admin_required
def search_tags():
    q = (request.args.get("q") or "").strip()
    page = max(int(request.args.get("page", 1)), 1)
    per_page = 20

    query = Tag.query.order_by(Tag.name.asc())

    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                Tag.name.ilike(like),
                Tag.slug.ilike(like),
            )
        )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return {
        "results": [
            {"value": tag.id, "text": f"{tag.name} ({tag.slug})"}
            for tag in pagination.items
        ],
        "has_more": pagination.has_next,
    }

@api_bp.get("/assets")
@login_required
@admin_required
def search_assets():
    q = (request.args.get("q") or "").strip()
    page = max(int(request.args.get("page", 1)), 1)
    per_page = 20

    query = Asset.query.order_by(Asset.created_at.desc())

    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                Asset.path.ilike(like),
                Asset.alt_text.ilike(like),
                Asset.caption.ilike(like),
            )
        )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return {
        "results": [
            {
                "value": asset.id,
                "text": asset.path,
                "path": asset.path,
                "alt_text": asset.alt_text or "",
                "caption": asset.caption or "",
            }
            for asset in pagination.items
        ],
        "has_more": pagination.has_next,
    }
