import os
from app import db
from app.models import  ArticleAsset, ProjectAsset
from app.blueprints.admin.services.assets.asset_cleanup import generate_unique_filepath, split_asset_path

def delete_asset_file(db_path: str):
    absolute_path = _db_asset_path_to_filesystem(db_path)

    if absolute_path and os.path.exists(absolute_path):
        os.remove(absolute_path)

def delete_asset_if_unused(asset):
    if asset is None:
        return

    if _asset_is_still_used(asset.id):
        return

    delete_asset_file(asset.path)
    db.session.delete(asset)

def save_uploaded_asset(uploaded_file, raw_path: str):
    if not uploaded_file:
        raise ValueError("No file provided.")

    path_info = _build_asset_storage_paths(raw_path)
    unique_filename = generate_unique_filepath(path_info["target_dir"], path_info["safe_filename"])
    absolute_path = os.path.join(path_info["target_dir"], unique_filename)

    uploaded_file.save(absolute_path)

    db_path = f"/static/{os.path.relpath(absolute_path, os.path.join('app', 'static')).replace(os.sep, '/')}"
    return db_path, absolute_path

def _build_asset_storage_paths(raw_path: str):
    normalized, relative_path, relative_dir, safe_filename = split_asset_path(raw_path)

    static_root = os.path.join("app", "static")
    target_dir = os.path.join(static_root, relative_dir.replace("uploads/", "uploads/", 1))
    os.makedirs(target_dir, exist_ok=True)

    return {
        "db_path": f"/static/{relative_dir}/{safe_filename}",
        "target_dir": target_dir,
        "safe_filename": safe_filename,
    }

def _db_asset_path_to_filesystem(db_path: str):
    if not db_path:
        return None

    cleaned = db_path.lstrip("/")
    if not cleaned.startswith("static/"):
        return None

    return os.path.join("app", cleaned)

def _asset_is_still_used(asset_id: int) -> bool:
    article_use = db.session.query(ArticleAsset).filter_by(asset_id=asset_id).first()
    if article_use:
        return True

    project_use = db.session.query(ProjectAsset).filter_by(asset_id=asset_id).first()
    if project_use:
        return True

    return False
