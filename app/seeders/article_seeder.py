from faker import Faker
from app.seeders.base import BaseSeeder
from app.models import Article, ArticleTag, ArticleCategory, ArticleAsset, Tag, Category, Asset, User
from app.models.base import Status
from app.extensions import db
from app.models.utils import utc_now
from app.seeders.article_seed_data import ARTICLES

fake = Faker()
Faker.seed(42)

def _get_or_warn(model, field, value):
    # Fetch a record by field value, print warning if missing.
    record = db.session.query(model).filter(
            getattr(model, field) == value
    ).first()
    if not record:
        print(f"[ArticleSeeder] {model.__name__} with {field}='{value}' not found - skipping")
    return record

def _seed_article_joins(article, data):
    author = db.session.query(User).first()

    # Tags
    for i, tag_name in enumerate(data.get("tags", [])):
        tag = _get_or_warn(Tag, "name", tag_name)
        if tag:
            db.session.add(ArticleTag(
                article_id=article.id,
                tag_id=tag.id,
                sort_order=i
            ))

    # Category
    category = _get_or_warn(Category, "name", data.get("category"))
    if category:
        db.session.add(ArticleCategory(
            article_id=article.id,
            category_id=category.id,
            sort_order=0,
            is_primary=True
        ))

    # Cover asset
    cover = _get_or_warn(Asset, "path", data.get("cover"))
    if cover:
        db.session.add(ArticleAsset(
            article_id=article.id,
            asset_id=cover.id,
            role="cover",
            is_cover=True
        ))

    # Inline assets
    for asset_path in data.get("inline_assets", []):
        asset = _get_or_warn(Asset, "path", asset_path)
        if asset:
            db.session.add(ArticleAsset(
                article_id=article.id,
                asset_id=asset.id,
                role="inline",
                is_cover=False
            ))

    # Diagrams
    for asset_path in data.get("diagrams", []):
        asset = _get_or_warn(Asset, "path", asset_path)
        if asset:
            db.session.add(ArticleAsset(
                article_id=article.id,
                asset_id=asset.id,
                role="diagram",
                is_cover=False
            ))

    # Attachments
    for asset_path in data.get("attachments", []):
        asset = _get_or_warn(Asset, "path", asset_path)
        if asset:
            db.session.add(ArticleAsset(
                article_id=article.id,
                asset_id=asset.id,
                role="attachment",
                is_cover=False
            ))

class ArticleSeeder(BaseSeeder):
    def run(self):
        seen_slug = set()

        author = db.session.query(User).first()
        if not author:
            print("[ArticleSeeder] No users found. Run UserSeeder first")
            return
        created = 0
        skipped = 0
        for data in ARTICLES:
            if data["slug"] in seen_slug:
                print(f"[ArticleSeeder] Duplicate slug in the data: 'data['slug']' - skipping")
                continue
            seen_slug.add(data["slug"])
            exists = db.session.query(Article).filter_by(slug=data["slug"]).first()
            if exists:
                skipped += 1
                continue
            article = Article(
                    title=data["title"],
                    slug=data["slug"],
                    excerpt=data["excerpt"],
                    body=data["body"],
                    read_time=data["read_time"],
                    is_featured=data["is_featured"],
                    status=Status(data["status"]),
                    published_at=utc_now() if data["status"] == "published" else None,
                    author_id=author.id,
                    seo_title=data.get("seo_title"),
                    seo_description=data.get("seo_description"),
            )
            db.session.add(article)
            db.session.flush()
            _seed_article_joins(article, data)
            created += 1
        db.session.commit()
        print(f"[ArticleSeeder] {created} created, {skipped} skipped")
