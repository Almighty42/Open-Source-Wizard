from app.extensions import db

class BaseSeeder:
    def run(self):
        raise NotImplementedError

    def save(self, *instances):
        db.session.add_all(instances)
        db.session.commit()
