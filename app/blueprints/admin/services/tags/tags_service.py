from app import db
from app.blueprints.admin.exceptions import TagCreateError
from app.models import Tag

def create_tag(form_data) -> Tag:
    try:
        tag = Tag(
            name=form_data.name.data.strip(),
            slug=form_data.slug.data.strip(),
            description=form_data.description.data.strip() if form_data.description.data else None,
            seo_title=form_data.seo_title.data.strip() if form_data.seo_title.data else None,
            seo_description=form_data.seo_description.data.strip() if form_data.seo_description.data else None,
        )

        db.session.add(tag)
        db.session.commit()

        return tag

    except Exception:
        db.session.rollback()
        raise TagCreateError()
