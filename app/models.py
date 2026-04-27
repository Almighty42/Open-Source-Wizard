from app import db, login_manager
from flask_login import UserMixin
import sqlalchemy as sql
import sqlalchemy.orm as orm
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    username: orm.Mapped[str] = orm.mapped_column(sql.String(64), index=True, unique= True)
    password_hash: orm.Mapped[str] = orm.mapped_column(sql.String(256))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(id):
    return db.session.get(User, int(id))
