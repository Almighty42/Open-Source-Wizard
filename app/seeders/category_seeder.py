from faker import Faker
from app.seeders.base import BaseSeeder
from app.models import Category
from app.extensions import db

fake = Faker()

CORE_CATEGORIES = [
        { "name": "Embedded Systems", "slug": "embedded-systems", "description": "Embedded Systems" },
        { "name": "Linux", "slug": "linux", "description": "Linux" },
        { "name": "Self-Hosting", "slug": "self-hosting", "description": "Self Hosting" },
        {"name": "Reverse Engineering", "slug": "reverse-engineering", "description": "Reverse Engineering"},
        {"name": "Hardware", "slug": "hardware", "description": "Hardware"},
        {"name": "Notes", "slug": "notes", "description": "Notes"},
        ]

class CategorySeeder(BaseSeeder):
    def run(self):
        created = 0
        skipped = 0
        for data in CORE_CATEGORIES:
            exists = db.session.query(Category).filter_by(slug=data["slug"]).first()
            if exists:
                skipped += 1
                continue
            category = Category(
                    name=data["name"],
                    slug=data["slug"],
                    description=data["description"],
                    seo_title=f"{data['name']} - Articles & Projects",
                    seo_description=data["description"]
            )
            db.session.add(category)
            created += 1
        db.session.commit()
        print(f"[CategorySeeder] {created} created, {skipped} skipped.")
