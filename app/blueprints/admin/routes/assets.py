from flask import render_template, flash, redirect, url_for
from app import db
from app.models import Asset
from app.forms import AssetForm, DeleteForm
from app.decorators import admin_required
from app.blueprints.admin import admin_bp
from app.blueprints.admin.services import create_asset
from app.blueprints.admin.exceptions import AssetCreateError, AssetDeleteError
import sqlalchemy as sql

@admin_bp.route("/add-asset", methods=["GET", "POST"])
@admin_required
def add_asset():
    form = AssetForm()

    if form.validate_on_submit():
        try:
            create_asset(form)
            return redirect(url_for("admin.add_asset"))
        except AssetCreateError as e:
            flash(f"{e.message}")
    elif form.is_submitted():
        flash("Please fix the errors in the form.", "error")

    return render_template(
        "admin/add-asset.html",
        form=form,
        title="Add Asset",
    )

@admin_bp.route("/assets")
@admin_required
def assets():
    assets = db.session.scalars(sql.select(Asset).order_by(Asset.created_at.desc())).all()
    delete_form = DeleteForm()
    return render_template("admin/assets.html", title="Assets", assets=assets, delete_form=delete_form)

@admin_bp.route("/delete-asset/<int:asset_id>", methods=["POST"])
@admin_required
def delete_asset(asset_id):
    delete_form = DeleteForm()

    if not delete_form.validate_on_submit():
        flash("Invalid request.", "error")
        return redirect(url_for("admin.assets"))

    asset = db.session.get(Asset, asset_id)

    if not asset:
        flash("Asset not found.", "error")
        return redirect(url_for("admin.assets"))

    if asset.article_assets or asset.project_assets:
        flash(f"Cannot delete '{asset.path}' — it is still used by articles or projects.", "error")
        return redirect(url_for("admin.assets"))

    try:
        db.session.delete(asset)
        db.session.commit()
        flash(f"Asset '{asset.path}' deleted.", "success")
    except Exception as e:
        db.session.rollback()
        raise AssetDeleteError(message="Failed to delete asset.", details=str(e))

    return redirect(url_for("admin.assets"))
