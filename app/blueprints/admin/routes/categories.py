from flask import  render_template, flash, redirect, url_for
from app.blueprints.admin.exceptions import CategoryCreateError
from app.blueprints.admin.services import create_category
from app.decorators import admin_required
from app.blueprints.admin import admin_bp
from app.forms import CategoryForm

@admin_bp.route("/add-category", methods=["GET", "POST"])
@admin_required
def add_category():
    form = CategoryForm()

    if form.validate_on_submit():
        try:
            create_category(form)
            flash("Category created successfully.", "success")
            return redirect(url_for("admin.add_category"))
        except CategoryCreateError as e:
            flash(f"{e.message}")
    elif form.is_submitted():
        flash("Please fix the errors in the form.", "error")

    return render_template(
            "admin/add-category.html",
            form=form,
            title="Add Category",
            )
