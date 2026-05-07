from app import db
from app.blueprints.admin.exceptions import AssetCreateError, AssetUpdateError
from app.blueprints.admin.services.assets.asset_storage import save_uploaded_asset, delete_asset_file
from app.blueprints.admin.services.assets.asset_cleanup import split_asset_path
from app.models import Asset

def create_asset(form_data) -> Asset:
    try:
        uploaded_file = form_data.file.data
        db_path, _absolute_path = save_uploaded_asset(
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
        _, _, relative_dir, safe_filename = split_asset_path(requested_raw_path)
        requested_db_path = f"static/{relative_dir}/{safe_filename}"

        if requested_db_path != old_db_path and not form_data.file.data:
            raise AssetUpdateError("Please upload a new file when changing the asset path.", "User tried to upload the same file")
            # return redirect(url_for("admin.edit_asset", asset_id=asset.id))

        if form_data.file.data:
            new_db_path, _absolute_path = save_uploaded_asset(form_data.file.data, requested_raw_path)
            asset.path = new_db_path
        else:
            asset.path = old_db_path

        asset.alt_text = form_data.alt_text.data.strip() if form_data.alt_text.data else None
        asset.caption = form_data.caption.data.strip() if form_data.caption.data else None

        db.session.commit()

        if form_data.file.data and old_db_path != asset.path:
            delete_asset_file(old_db_path)

        return asset

    except Exception:
        db.session.rollback()
        raise AssetUpdateError("Something went wrong while trying to create the asset, try again")
