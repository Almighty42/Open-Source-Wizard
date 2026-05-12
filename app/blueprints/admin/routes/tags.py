from flask import  render_template, flash, url_for, redirect
from app import db
from app.models import Tag
from app.forms import TagForm, DeleteForm
from app.decorators import admin_required
from app.blueprints.admin import admin_bp
from app.blueprints.admin.services import create_tag
from app.blueprints.admin.exceptions import TagCreateError, TagDeleteError
import sqlalchemy as sql

@admin_bp.route("/add-tag", methods=["GET", "POST"])
@admin_required
def add_tag():
    form = TagForm()

    if form.validate_on_submit():
        try:
            create_tag(form)
            flash("Tag created successfully.", "success")
            return redirect(url_for("admin.add_tag"))
        except TagCreateError as e:
            flash(f"{e.message}")
    elif form.is_submitted():
        flash("Please fix the errors in the form.", "error")

    return render_template(
            "admin/add-tag.html", 
            form=form,
            title="Add Tag",
            )

@admin_bp.route("/tags")
@admin_required
def tags():
    tags = db.session.scalars(sql.select(Tag).order_by(Tag.name)).all()
    delete_form = DeleteForm()
    return render_template("admin/tags.html", title="Tags", tags=tags, delete_form=delete_form)

@admin_bp.route("/delete-tag/<int:tag_id>", methods=["POST"])
@admin_required
def delete_tag(tag_id):
    delete_form = DeleteForm()

    if not delete_form.validate_on_submit():
        flash("Invalid request.", "error")
        return redirect(url_for("admin.tags"))

    tag = db.session.get(Tag, tag_id)

    if not tag:
        flash("Tag not found.", "error")
        return redirect(url_for("admin.tags"))

    try:
        db.session.delete(tag)
        db.session.commit()
        flash(f"Tag '{tag.name}' deleted.", "success")
    except Exception as e:
        db.session.rollback()
        raise TagDeleteError(message="Failed to delete tag.", details=str(e))

    return redirect(url_for("admin.tags"))
