from flask import flash, redirect, url_for
from app import db
from app.models import Tag

def add_tag_db(form_data):
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

        flash("Tag created successfully.", "success")
        return redirect(url_for("admin.add_tag"))

    except Exception:
        db.session.rollback()
        flash("Failed to create tag.", "error")
