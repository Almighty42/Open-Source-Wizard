# TODO: REFACTOR
import os
from werkzeug.utils import secure_filename
from app.models import (
    Category,
    Tag,
    Asset,
    Article,
    Project,
    ArticleTag,
    ArticleCategory,
    ArticleAsset,
    ProjectTag,
    ProjectCategory,
    ProjectAsset
)
from flask import redirect, url_for, flash
from app.utils import calculate_read_time
from app import db
from flask_login import current_user

def fetch_categories() -> list[Category]:
    return Category.query.order_by(Category.name).all()

def fetch_tags() -> list[Tag]:
    return Tag.query.order_by(Tag.name).all()

def fetch_assets() -> list[Asset]:
    return Asset.query.order_by(Asset.path).all()

def build_category_choices(categories):
    return [("", "Select category")] + [
        (category.slug, category.name) for category in categories
    ]

def build_tag_choices(tags):
    return [
        (tag.slug, tag.name) for tag in tags
    ]

def build_cover_asset_choices(assets):
    return [(None, "No cover")] + [
        (asset.id, asset.path) for asset in assets
    ]

def build_attachment_asset_choices(assets):
    return [
        (asset.id, asset.path) for asset in assets
    ]

def add_article_db(form_data):
    try:
        article = _build_article(form_data)
        selected_category = _get_selected_category(form_data)
        selected_tags = _get_selected_tags(form_data)
        cover_asset = _get_cover_asset(form_data)
        attachment_assets = _get_attachment_assets(form_data)

        db.session.add(article)
        db.session.flush()

        _add_article_category(article, selected_category)
        _add_article_tags(article, selected_tags)
        _add_article_assets(article, cover_asset, attachment_assets)

        db.session.commit()
        return redirect(url_for("article.article", slug=article.slug))

    except Exception:
        db.session.rollback()
        raise


def _build_article(form_data):
    return Article(
        title=form_data.title.data.strip(),
        slug=form_data.slug.data.strip(),
        body=form_data.body.data,
        status=form_data.status.data,
        published_at=form_data.published_at.data or None,
        excerpt=form_data.excerpt.data.strip(),
        read_time=calculate_read_time(form_data.body.data),
        author_id=current_user.id,
        seo_title=form_data.title.data.strip(),
        seo_description=form_data.excerpt.data.strip(),
    )


def _get_selected_category(form_data):
    if not form_data.category.data:
        return None

    return Category.query.filter_by(slug=form_data.category.data).first()


def _get_selected_tags(form_data):
    if not form_data.tags.data:
        return []

    return Tag.query.filter(Tag.slug.in_(form_data.tags.data)).all()


def _get_cover_asset(form_data):
    if not form_data.cover_asset.data:
        return None

    return db.session.get(Asset, form_data.cover_asset.data)


def _get_attachment_assets(form_data):
    if not form_data.attachment_assets.data:
        return []

    return Asset.query.filter(
        Asset.id.in_(form_data.attachment_assets.data)
    ).all()


def _add_article_category(article, category):
    if not category:
        return

    article.article_categories.append(
        ArticleCategory(
            category_id=category.id,
            is_primary=True,
        )
    )


def _add_article_tags(article, tags):
    for index, tag in enumerate(tags):
        article.article_tags.append(
            ArticleTag(
                tag_id=tag.id,
                sort_order=index,
            )
        )


def _add_article_assets(article, cover_asset, attachment_assets):
    if cover_asset:
        article.article_assets.append(
            ArticleAsset(
                asset_id=cover_asset.id,
                role="cover",
            )
        )

    for index, asset in enumerate(attachment_assets, start=1):
        if cover_asset and asset.id == cover_asset.id:
            continue

        article.article_assets.append(
            ArticleAsset(
                asset_id=asset.id,
                role="attachment",
            )
        )

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

def add_category_db(form_data):
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

        flash("Category created successfully.", "success")
        return redirect(url_for("admin.add_category"))

    except Exception:
        db.session.rollback()
        flash("Failed to create category.", "error")

def update_article_db(article, form_data):
    try:
        selected_category = _get_selected_category(form_data)
        selected_tags = _get_selected_tags(form_data)
        cover_asset = _get_cover_asset(form_data)
        attachment_assets = _get_attachment_assets(form_data)

        article.title = form_data.title.data.strip()
        article.slug = form_data.slug.data.strip()
        article.body = form_data.body.data
        article.status = form_data.status.data
        article.published_at = form_data.published_at.data or None
        article.excerpt = form_data.excerpt.data.strip()
        article.is_featured = form_data.is_featured.data
        article.read_time = calculate_read_time(form_data.body.data)
        article.seo_title = form_data.title.data.strip()
        article.seo_description = form_data.excerpt.data.strip()

        article.article_categories.clear()
        article.article_tags.clear()
        article.article_assets.clear()

        _add_article_category(article, selected_category)
        _add_article_tags(article, selected_tags)
        _add_article_assets(article, cover_asset, attachment_assets)

        db.session.commit()
        flash("Article updated successfully.", "success")
        return redirect(url_for("article.article", slug=article.slug))

    except Exception:
        db.session.rollback()
        raise

def update_project_db(project, form_data):
    try:
        selected_category = _get_selected_category(form_data)
        selected_tags = _get_selected_tags(form_data)
        cover_asset = _get_cover_asset(form_data)
        attachment_assets = _get_attachment_assets(form_data)

        project.title = form_data.title.data.strip()
        project.slug = form_data.slug.data.strip()
        project.status = form_data.status.data
        project.project_state = form_data.project_state.data
        project.platform = form_data.platform.data.strip() if form_data.platform.data else None
        project.repo_url = form_data.repo_url.data.strip() if form_data.repo_url.data else None
        project.demo_url = form_data.demo_url.data.strip() if form_data.demo_url.data else None
        project.is_featured = bool(form_data.is_featured.data)

        project.excerpt = form_data.excerpt.data.strip()
        project.body = form_data.body.data

        project.published_at = form_data.published_at.data or None
        project.started_at = form_data.started_at.data or None
        project.completed_at = form_data.completed_at.data or None

        project.seo_title = form_data.title.data.strip()
        project.seo_description = form_data.excerpt.data.strip()

        project.project_categories.clear()
        project.project_tags.clear()
        project.project_assets.clear()

        _add_project_category(project, selected_category)
        _add_project_tags(project, selected_tags)
        _add_project_assets(project, cover_asset, attachment_assets)

        db.session.commit()
        flash("Project updated successfully.", "success")
        return redirect(url_for("project.project", slug=project.slug))

    except Exception:
        db.session.rollback()
        raise


def _add_project_category(project, selected_category):
    if not selected_category:
        return

    project.project_categories.append(
        ProjectCategory(project=project, category=selected_category)
    )

def _add_project_tags(project, selected_tags):
    if not selected_tags:
        return

    for tag in selected_tags:
        project.project_tags.append(
            ProjectTag(project=project, tag=tag)
        )


def _add_project_assets(project, cover_asset, attachment_assets):
    if cover_asset:
        project.project_assets.append(
            ProjectAsset(
                project=project,
                asset=cover_asset,
                is_cover=True,
                role="cover",
            )
        )

    for asset in attachment_assets:
        if cover_asset and asset.id == cover_asset.id:
            continue

        project.project_assets.append(
            ProjectAsset(
                project=project,
                asset=asset,
                is_cover=False,
                role="attachment",
            )
        )

def add_asset_db(form_data):
    try:
        uploaded_file = form_data.file.data
        db_path, _absolute_path = _save_uploaded_asset(uploaded_file, form_data.path.data.strip())

        asset = Asset(
            path=db_path,
            alt_text=form_data.alt_text.data.strip() if form_data.alt_text.data else None,
            caption=form_data.caption.data.strip() if form_data.caption.data else None,
        )

        db.session.add(asset)
        db.session.commit()

        flash("Asset created successfully.", "success")
        return redirect(url_for("admin.add_asset"))

    except Exception:
        db.session.rollback()
        flash("Failed to create asset.", "error")
        raise

def update_asset_db(asset, form_data):
    old_db_path = asset.path
    requested_raw_path = form_data.path.data.strip()

    try:
        _, _, relative_dir, safe_filename = _split_asset_path(requested_raw_path)
        requested_db_path = f"/static/{relative_dir}/{safe_filename}"

        if requested_db_path != old_db_path and not form_data.file.data:
            flash("Please upload a new file when changing the asset path.", "error")
            return redirect(url_for("admin.edit_asset", asset_id=asset.id))

        if form_data.file.data:
            new_db_path, _absolute_path = _save_uploaded_asset(form_data.file.data, requested_raw_path)
            asset.path = new_db_path
        else:
            asset.path = old_db_path

        asset.alt_text = form_data.alt_text.data.strip() if form_data.alt_text.data else None
        asset.caption = form_data.caption.data.strip() if form_data.caption.data else None

        db.session.commit()

        if form_data.file.data and old_db_path != asset.path:
            _delete_asset_file(old_db_path)

        flash("Asset updated successfully.", "success")
        return redirect(url_for("admin.edit_asset", asset_id=asset.id))

    except Exception:
        db.session.rollback()
        flash("Failed to update asset.", "error")
        raise


def _normalize_asset_path(raw_path: str) -> str:
    raw_path = raw_path.strip()

    if not raw_path.startswith("/uploads/"):
        raise ValueError("Path must start with /uploads/.")

    return raw_path


def _build_asset_storage_paths(raw_path: str):
    normalized, relative_path, relative_dir, safe_filename = _split_asset_path(raw_path)

    static_root = os.path.join("app", "static")
    target_dir = os.path.join(static_root, relative_dir.replace("uploads/", "uploads/", 1))
    os.makedirs(target_dir, exist_ok=True)

    return {
        "db_path": f"/static/{relative_dir}/{safe_filename}",
        "target_dir": target_dir,
        "safe_filename": safe_filename,
    }

def _generate_unique_filepath(directory: str, filename: str):
    name, ext = os.path.splitext(filename)
    candidate = filename
    counter = 1

    while os.path.exists(os.path.join(directory, candidate)):
        candidate = f"{name}-{counter}{ext}"
        counter += 1

    return candidate


def _save_uploaded_asset(uploaded_file, raw_path: str):
    if not uploaded_file:
        raise ValueError("No file provided.")

    path_info = _build_asset_storage_paths(raw_path)
    unique_filename = _generate_unique_filepath(path_info["target_dir"], path_info["safe_filename"])
    absolute_path = os.path.join(path_info["target_dir"], unique_filename)

    uploaded_file.save(absolute_path)

    db_path = f"/static/{os.path.relpath(absolute_path, os.path.join('app', 'static')).replace(os.sep, '/')}"
    return db_path, absolute_path


def _db_asset_path_to_filesystem(db_path: str):
    if not db_path:
        return None

    cleaned = db_path.lstrip("/")
    if not cleaned.startswith("static/"):
        return None

    return os.path.join("app", cleaned)


def _delete_asset_file(db_path: str):
    absolute_path = _db_asset_path_to_filesystem(db_path)

    if absolute_path and os.path.exists(absolute_path):
        os.remove(absolute_path)


def _split_asset_path(raw_path: str):
    normalized = _normalize_asset_path(raw_path)
    relative_path = normalized.lstrip("/")
    relative_dir = os.path.dirname(relative_path)
    original_filename = os.path.basename(relative_path)
    safe_filename = secure_filename(original_filename)

    if not safe_filename:
        raise ValueError("Invalid file name.")

    return normalized, relative_path, relative_dir, safe_filename

def add_project_db(form_data):
    try:
        project = _build_project(form_data)
        selected_category = _get_selected_category(form_data)
        selected_tags = _get_selected_tags(form_data)
        cover_asset = _get_cover_asset(form_data)
        attachment_assets = _get_attachment_assets(form_data)

        db.session.add(project)
        db.session.flush()

        _add_project_category(project, selected_category)
        _add_project_tags(project, selected_tags)
        _add_project_assets(project, cover_asset, attachment_assets)

        db.session.commit()
        return redirect(url_for("project.project", slug=project.slug))

    except Exception:
        db.session.rollback()
        raise

def _build_project(form_data):
    return Project(
        title=form_data.title.data.strip(),
        slug=form_data.slug.data.strip(),
        status=form_data.status.data,
        project_state=form_data.project_state.data,
        platform=form_data.platform.data.strip() if form_data.platform.data else None,
        repo_url=form_data.repo_url.data.strip() if form_data.repo_url.data else None,
        demo_url=form_data.demo_url.data.strip() if form_data.demo_url.data else None,
        is_featured=bool(form_data.is_featured.data),
        excerpt=form_data.excerpt.data.strip(),
        body=form_data.body.data,
        published_at=form_data.published_at.data or None,
        started_at=form_data.started_at.data or None,
        completed_at=form_data.completed_at.data or None,
        author_id=current_user.id,
        seo_title=form_data.title.data.strip(),
        seo_description=form_data.excerpt.data.strip(),
    )
