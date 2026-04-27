from datetime import datetime, timedelta
from app import db, login_manager
from flask_login import UserMixin
import sqlalchemy as sql
import sqlalchemy.orm as orm
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    username: orm.Mapped[str] = orm.mapped_column(sql.String(64), index=True, unique= True)
    password_hash: orm.Mapped[str] = orm.mapped_column(sql.String(256))
    login_attempts: orm.Mapped[int] = orm.mapped_column(default=0, nullable=False)
    locked_out_until: orm.Mapped[datetime | None] = orm.mapped_column(sql.DateTime(), nullable=True)
    is_admin: orm.Mapped[bool] = orm.mapped_column(default=False, nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def toggle_admin(self, password):
        if self.check_password(password):
            self.is_admin = True
        return self.is_admin

    def is_locked_out(self):
        return self.locked_out_until is not None and datetime.now() < self.locked_out_until

    def lock_user(self):
        self.locked_out_until = datetime.now() + timedelta(minutes=10)

    def __repr__(self) :
        return f"<User {self.username}>"

@login_manager.user_loader
def load_user(id):
    return db.session.get(User, int(id))
