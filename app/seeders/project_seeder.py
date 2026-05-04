from faker import Faker
from app.models.project import ProjectState
from app.seeders.base import BaseSeeder
from app.models import Project, ProjectTag, ProjectCategory, ProjectAsset, Tag, Category, Asset, User
from app.seeders.project_seed_data import PROJECTS
from app.models.base import Status
from app.extensions import db
from app.utils import utc_now

fake = Faker()
Faker.seed(42)

def _get_or_warn(model, field, value):
    record = db.session.query(model).filter(
        getattr(model, field) == value
    ).first()
    if not record:
        print(f"[ProjectSeeder] {model.__name__} with {field}='{value}' not found — skipping.")
    return record

def _seed_project_joins(project, data):
    # Tags
    for i, tag_name in enumerate(data.get("tags", [])):
        tag = _get_or_warn(Tag, "name", tag_name)
        if tag:
            db.session.add(ProjectTag(
                project_id=project.id,
                tag_id=tag.id,
                sort_order=i,
            ))

    # Category
    category = _get_or_warn(Category, "name", data.get("category"))
    if category:
        db.session.add(ProjectCategory(
            project_id=project.id,
            category_id=category.id,
            sort_order=0,
            is_primary=True,
        ))

    # Cover
    cover = _get_or_warn(Asset, "path", data.get("cover"))
    if cover:
        db.session.add(ProjectAsset(
            project_id=project.id,
            asset_id=cover.id,
            role="cover",
            is_cover=True,
        ))

    # Gallery
    for asset_path in data.get("gallery", []):
        asset = _get_or_warn(Asset, "path", asset_path)
        if asset:
            db.session.add(ProjectAsset(
                project_id=project.id,
                asset_id=asset.id,
                role="gallery",
                is_cover=False,
            ))

    # Attachments
    for asset_path in data.get("attachments", []):
        asset = _get_or_warn(Asset, "path", asset_path)
        if asset:
            db.session.add(ProjectAsset(
                project_id=project.id,
                asset_id=asset.id,
                role="attachment",
                is_cover=False,
            ))

class ProjectSeeder(BaseSeeder):
    def run(self):
        author = db.session.query(User).first()
        if not author:
            print("[ProjectSeeder] No users found. Run UserSeeder first.")
            return

        created = 0
        skipped = 0

        for data in PROJECTS:
            exists = db.session.query(Project).filter_by(slug=data["slug"]).first()
            if exists:
                skipped += 1
                continue

            project = Project(
                title=data["title"],
                slug=data["slug"],
                excerpt=data["excerpt"],
                body=data["body"],
                is_featured=data["is_featured"],
                status=Status(data["status"]),
                published_at=utc_now() if data["status"] == "published" else None,
                project_state=ProjectState(data["project_state"]),
                platform=data.get("platform"),
                repo_url=data.get("repo_url"),
                demo_url=data.get("demo_url"),
                author_id=author.id,
                seo_title=data.get("seo_title"),
                seo_description=data.get("seo_description"),
            )
            db.session.add(project)
            db.session.flush()

            _seed_project_joins(project, data)
            created += 1

        db.session.commit()
        print(f"[ProjectSeeder] {created} created, {skipped} skipped.")
