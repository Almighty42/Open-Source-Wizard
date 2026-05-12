from flask import render_template, flash, redirect, url_for
from flask_login import current_user
from app import db
from app.models import Category
from app.blueprints.admin.exceptions import CategoryCreateError, CategoryDeleteError
from app.blueprints.admin.services import create_category
from app.decorators import admin_required
from app.blueprints.admin import admin_bp
from app.forms import CategoryForm, DeleteForm
import sqlalchemy as sql

import logging
logger =  logging.getLogger(__name__)

@admin_bp.route("/add-category", methods=["GET", "POST"])
@admin_required
def add_category():
    form = CategoryForm()

    if form.validate_on_submit():
        try:
            create_category(form)
            flash("Category created successfully.", "success")
            logger.info("Category created: slug=%s user=%s", form.slug, current_user.id)
            return redirect(url_for("admin.add_category"))
        except CategoryCreateError as e:
            flash(f"{e.message}")
            logger.error("Failed to create category: slug=%s, message=%s, details=%s", form.slug, e.message, e.details, exc_info=True)
    elif form.is_submitted():
        flash("Please fix the errors in the form.", "error")

    return render_template(
        "admin/add-category.html",
        form=form,
        title="Add Category",
    )

@admin_bp.route("/categories")
@admin_required
def categories():
    categories = db.session.scalars(sql.select(Category).order_by(Category.sort_order, Category.name)).all()
    delete_form = DeleteForm()
    return render_template("admin/categories.html", title="Categories", categories=categories, delete_form=delete_form)

@admin_bp.route("/delete-category/<int:category_id>", methods=["POST"])
@admin_required
def delete_category(category_id):
    delete_form = DeleteForm()

    if not delete_form.validate_on_submit():
        flash("Invalid request.", "error")
        return redirect(url_for("admin.categories"))

    category = db.session.get(Category, category_id)

    if not category:
        flash("Category not found.", "error")
        return redirect(url_for("admin.categories"))

    try:
        db.session.delete(category)
        db.session.commit()
        flash(f"Category '{category.name}' deleted.", "success")
        logger.warning("Category deleted: id=%s user=%s", category.id, )
    except Exception as e:
        db.session.rollback()
        logger.error("Failed to delete category, id=%s",category.id, exc_info=True)
        raise CategoryDeleteError(message="Failed to delete category.", details=str(e))

    return redirect(url_for("admin.categories"))
