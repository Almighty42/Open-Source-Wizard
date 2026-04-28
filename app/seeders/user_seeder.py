from app.models import User
from app.extensions import db
from app.seeders.base import BaseSeeder

ADMIN_USERNAME = ""
ADMIN_PASSWORD = ""

class UserSeeder(BaseSeeder):
    def run(self):
        exists = db.session.query(User).filter_by(username=ADMIN_USERNAME).first()
        if exists:
            print(f"[UserSeeder] Admin '{ADMIN_USERNAME} already exists, skipping'")
            return
        admin = User(
                username=ADMIN_USERNAME,
                is_admin=True,
                login_attempts=0
        )
        admin.set_password(ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()
        print(f"[UserSeeder] Admin user '{ADMIN_USERNAME}' created")
        print(f"[UserSeeder] Default password for admin user is '{ADMIN_PASSWORD}'")
