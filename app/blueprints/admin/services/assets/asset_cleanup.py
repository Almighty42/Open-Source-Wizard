import os
from werkzeug.utils import secure_filename

def generate_unique_filepath(directory: str, filename: str):
    name, ext = os.path.splitext(filename)
    candidate = filename
    counter = 1

    while os.path.exists(os.path.join(directory, candidate)):
        candidate = f"{name}-{counter}{ext}"
        counter += 1

    return candidate

def split_asset_path(raw_path: str):
    normalized = _normalize_asset_path(raw_path)
    relative_path = normalized.lstrip("/")
    relative_dir = os.path.dirname(relative_path)
    original_filename = os.path.basename(relative_path)
    safe_filename = secure_filename(original_filename)

    if not safe_filename:
        raise ValueError("Invalid file name.")

    return normalized, relative_path, relative_dir, safe_filename

def _normalize_asset_path(raw_path: str) -> str:
    raw_path = raw_path.strip()

    if not raw_path.startswith("/uploads/"):
        raise ValueError("Path must start with /uploads/.")

    return raw_path

