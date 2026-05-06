from flask import  render_template, flash, redirect, url_for
from app.forms import AssetForm
from app.decorators import admin_required
from app.blueprints.admin import admin_bp
from app.blueprints.admin.services import create_asset
from app.blueprints.admin.exceptions import AssetCreateError

@admin_bp.route("/add-asset", methods=["GET", "POST"])
@admin_required
def add_asset():
    form = AssetForm()

    if form.validate_on_submit():
        try:
            create_asset(form)
            return redirect(url_for("admin.add_asset"))
        except AssetCreateError as e:
            # TODO: LOGGING
            flash(f"{e.message}")
    elif form.is_submitted():
        flash("Please fix the errors in the form.", "error")

    return render_template(
            "admin/add-asset.html",
            form=form,
            title="Add Asset",
            )
