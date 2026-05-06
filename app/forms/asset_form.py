import os
from app.models import Asset

from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    FileField,
)
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Optional, Length, ValidationError

class AssetForm(FlaskForm):
    ALLOWED_ASSET_EXTENSIONS = [
        "jpg", "jpeg", "png", "webp", "gif", "svg", "avif",
        "pdf", "txt", "md", "rtf",
        "json", "csv", "tsv", "xml", "yaml", "yml",
        "c", "h", "cpp", "hpp", "py", "js", "ts", "css", "html", "sql",
        "zip", "tar", "gz", "bz2", "xz", "7z",
        "mp3", "wav", "ogg", "mp4", "webm",
        "epub",
    ]

    def __init__(self, original_asset=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_asset = original_asset

    file = FileField(
        "File",
        validators=[
            FileAllowed(
                ALLOWED_ASSET_EXTENSIONS,
                "Unsupported file type."
            ),
        ],
    )

    path = StringField(
        "Path",
        validators=[
            DataRequired(),
            Length(min=3, max=128, message="Path must be between 3 and 128 characters."),
        ],
    )

    alt_text = StringField(
        "Alt Text",
        validators=[
            Optional(),
            Length(max=64, message="Alt text cannot be longer than 64 characters."),
        ],
    )

    caption = StringField(
        "Caption",
        validators=[
            Optional(),
            Length(max=64, message="Caption cannot be longer than 64 characters."),
        ],
    )

    submit = SubmitField("Add Asset")

    def validate(self, extra_validators=None):
        is_valid = super().validate(extra_validators=extra_validators)

        if self.original_asset is None and not self.file.data:
            self.file.errors.append("Please choose a file to upload.")
            is_valid = False

        if self.path.data and not self.path.data.strip().startswith("/uploads/"):
            self.path.errors.append("Path must start with /uploads/.")
            is_valid = False

        return is_valid

    @staticmethod
    def _normalize_asset_path(raw_path: str) -> str:
        raw_path = raw_path.strip()

        if not raw_path.startswith("/uploads/"):
            raise ValueError("Path must start with /uploads/ or /static/uploads/.")

        return raw_path

    @staticmethod
    def _split_asset_path(raw_path: str):
        normalized = AssetForm._normalize_asset_path(raw_path)
        relative_path = normalized.lstrip("/")
        relative_dir = os.path.dirname(relative_path)
        original_filename = os.path.basename(relative_path)
        safe_filename = secure_filename(original_filename)

        if not safe_filename:
            raise ValueError("Invalid file name.")

        return normalized, relative_path, relative_dir, safe_filename

    def validate_path(self, field):
        raw_path = (field.data or "").strip()

        if not raw_path.startswith("/uploads/") or not raw_path.startswith("/static/uploads/"):
            return
        try:
            _, _, relative_dir, safe_filename = AssetForm._split_asset_path(raw_path)
            normalized_db_path = f"/static/{relative_dir}/{safe_filename}"
        except ValueError:
            return

        existing = Asset.query.filter_by(path=normalized_db_path).first()

        if existing and (
            self.original_asset is None or existing.id != self.original_asset.id
        ):
            raise ValidationError("An asset with this path already exists.")

