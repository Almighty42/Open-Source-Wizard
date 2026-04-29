from faker import Faker
from app.seeders.base import BaseSeeder
from app.models import Tag
from app.extensions import db

fake = Faker()

CORE_TAGS = [
        { "name": "ESP32", "slug": "esp32", "description": "Projects and articles using the ESP32 microcontroller." },
        { "name": "Raspberry Pi", "slug": "raspberry-pi", "description": "Projects built on or around the Raspberry Pi." },
        {"name": "E-Ink",            "slug": "e-ink",             "description": "E-paper and e-ink display integration."},
        {"name": "C",                "slug": "c",                 "description": "Embedded C programming, patterns, and tips."},
        {"name": "Embedded",                "slug": "embedded",                 "description": "Embedded C programming, patterns, and tips."},
        {"name": "Python",           "slug": "python",            "description": "Python scripting, automation, and tooling."},
        {"name": "Docker",           "slug": "docker",            "description": "Containerization and Docker-based deployments."},
        {"name": "Nginx",            "slug": "nginx",             "description": "Nginx configuration, reverse proxying, and SSL."},
        {"name": "TinyML",           "slug": "tinyml",            "description": "Machine learning inference on microcontrollers."},
        {"name": "Power Management", "slug": "power-management",  "description": "Battery life, sleep modes, and low-power design."},
        {"name": "PCB",              "slug": "pcb",               "description": "PCB design, KiCad, and hardware layout."},
        {"name": "Debugging",        "slug": "debugging",         "description": "Debugging strategies for embedded and software."},
        {"name": "Linux",            "slug": "linux",             "description": "Linux system administration and tooling."},
        {"name": "AI",               "slug": "ai",                "description": "AI-assisted development and edge AI."},
        ]

class TagSeeder(BaseSeeder):
    def run(self):
        created = 0
        skipped = 0
        for data in CORE_TAGS:
            exists = db.session.query(Tag).filter_by(slug=data["slug"]).first()
            if exists:
                skipped += 1
                continue
            tag = Tag(
                    name=data["name"],
                    slug=data["slug"],
                    description=data["description"],
                    seo_title=f"{data['name']} - Articles & Projects",
                    seo_description=data["description"]
            )
            db.session.add(tag)
            created += 1
        db.session.commit()
        print(f"[TagSeeder] {created} created, {skipped} skipped.")
