@admin_bp.route("/add-category", methods=["GET", "POST"])
@admin_required
def add_category():
    form = CategoryForm()

    if form.validate_on_submit():
        services.add_category_db(form)
    elif form.is_submitted():
        flash("Please fix the errors in the form.", "error")

    return render_template(
            "admin/add-category.html",
            form=form,
            title="Add Category",
            )


