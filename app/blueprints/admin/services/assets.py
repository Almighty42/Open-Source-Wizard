import os
from app import db
from werkzeug.utils import secure_filename
from app.blueprints.admin.exceptions import ArticleUpdateError, AssetCreateError, AssetUpdateError
from app.models import Asset
import common

# NOTE: Main functions
def create_asset(form_data) -> Asset:
    try:
        uploaded_file = form_data.file.data
        db_path, _absolute_path = _save_uploaded_asset(
            uploaded_file,
            form_data.path.data.strip()
        )

        normalized_db_path = db_path.removeprefix("/")

        asset = Asset(
            path=normalized_db_path,
            alt_text=form_data.alt_text.data.strip() if form_data.alt_text.data else None,
            caption=form_data.caption.data.strip() if form_data.caption.data else None,
        )

        db.session.add(asset)
        db.session.commit()

        return asset

    except Exception:
        db.session.rollback()
        raise AssetCreateError()

def update_asset(asset, form_data) -> Asset:
    old_db_path = asset.path
    requested_raw_path = form_data.path.data.strip()

    try:
        _, _, relative_dir, safe_filename = _split_asset_path(requested_raw_path)
        requested_db_path = f"static/{relative_dir}/{safe_filename}"

        if requested_db_path != old_db_path and not form_data.file.data:
            raise ArticleUpdateError("Please upload a new file when changing the asset path.", "User tried to upload the same file")
            # return redirect(url_for("admin.edit_asset", asset_id=asset.id))

        if form_data.file.data:
            new_db_path, _absolute_path = _save_uploaded_asset(form_data.file.data, requested_raw_path)
            asset.path = new_db_path
        else:
            asset.path = old_db_path

        asset.alt_text = form_data.alt_text.data.strip() if form_data.alt_text.data else None
        asset.caption = form_data.caption.data.strip() if form_data.caption.data else None

        db.session.commit()

        if form_data.file.data and old_db_path != asset.path:
            common._delete_asset_file(old_db_path)

        return asset

    except Exception:
        db.session.rollback()
        raise AssetUpdateError("Something went wrong while trying to create the asset, try again")


# NOTE: Helper Functions
def _save_uploaded_asset(uploaded_file, raw_path: str):
    if not uploaded_file:
        raise ValueError("No file provided.")

    path_info = _build_asset_storage_paths(raw_path)
    unique_filename = _generate_unique_filepath(path_info["target_dir"], path_info["safe_filename"])
    absolute_path = os.path.join(path_info["target_dir"], unique_filename)

    uploaded_file.save(absolute_path)

    db_path = f"/static/{os.path.relpath(absolute_path, os.path.join('app', 'static')).replace(os.sep, '/')}"
    return db_path, absolute_path

def _generate_unique_filepath(directory: str, filename: str):
    name, ext = os.path.splitext(filename)
    candidate = filename
    counter = 1

    while os.path.exists(os.path.join(directory, candidate)):
        candidate = f"{name}-{counter}{ext}"
        counter += 1

    return candidate

def _normalize_asset_path(raw_path: str) -> str:
    raw_path = raw_path.strip()

    if not raw_path.startswith("/uploads/"):
        raise ValueError("Path must start with /uploads/.")

    return raw_path

def _split_asset_path(raw_path: str):
    normalized = _normalize_asset_path(raw_path)
    relative_path = normalized.lstrip("/")
    relative_dir = os.path.dirname(relative_path)
    original_filename = os.path.basename(relative_path)
    safe_filename = secure_filename(original_filename)

    if not safe_filename:
        raise ValueError("Invalid file name.")

    return normalized, relative_path, relative_dir, safe_filename

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
