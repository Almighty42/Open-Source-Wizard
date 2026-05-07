from app.models import Category, Tag, Asset

def fetch_categories() -> list[Category]:
    return Category.query.order_by(Category.name).all()

def fetch_tags() -> list[Tag]:
    return Tag.query.order_by(Tag.name).all()

def fetch_assets() -> list[Asset]:
    return Asset.query.order_by(Asset.path).all()
