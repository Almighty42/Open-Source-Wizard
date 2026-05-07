from flask import  render_template, flash, url_for, redirect
from app.forms import TagForm
from app.decorators import admin_required
from app.blueprints.admin import admin_bp
from app.blueprints.admin.services import create_tag
from app.blueprints.admin.exceptions import TagCreateError

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
