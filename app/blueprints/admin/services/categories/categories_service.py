from app import db
from app.blueprints.admin.exceptions import CategoryCreateError
from app.models import Category

def create_category(form_data):
    try:
        category = Category(
            name=form_data.name.data.strip(),
            slug=form_data.slug.data.strip(),
            description=form_data.description.data.strip() if form_data.description.data else None,
            seo_title=form_data.seo_title.data.strip() if form_data.seo_title.data else None,
            seo_description=form_data.seo_description.data.strip() if form_data.seo_description.data else None,
            sort_order=form_data.sort_order.data or 0,
        )

        db.session.add(category)
        db.session.commit()

        return category

    except Exception:
        db.session.rollback()
        raise CategoryCreateError()
