import os
from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    StringField,
    PasswordField,
    TextAreaField,
    SelectField,
    SelectMultipleField,
    SubmitField,
    BooleanField,
    FileField,
)
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Optional, Length, ValidationError, URL
from app.models import Article , Category, Tag, Asset
from werkzeug.utils import secure_filename

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

def int_or_none(value):
    if value in (None, "", "None"):
        return None
    return int(value)

class ArticleForm(FlaskForm):
    def __init__(self, original_article=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_article = original_article


    title = StringField(
        "Title",
        validators=[
            DataRequired(),
            Length(min=5, max=64, message="Title must be between 5 and 64 characters."),
        ],
    )

    slug = StringField(
        "Slug",
        validators=[
            DataRequired(),
            Length(min=5, max=64, message="Slug must be between 5 and 64 characters."),
        ],
    )

    status = SelectField(
        "Status",
        choices=[
            ("draft", "Draft"),
            ("published", "Published"),
            ("archived", "Archived"),
        ],
        validators=[DataRequired()],
    )

    excerpt = TextAreaField(
        "Short Description",
        validators=[
            DataRequired(),
            Length(min=20, max=300, message="Short description must be between 20 and 300 characters."),
        ],
    )

    is_featured = BooleanField("Featured")

    body = TextAreaField(
        "Markdown",
        validators=[
            DataRequired(),
            Length(min=100, message="Markdown must be at least 100 characters."),
        ],
    )

    category = SelectField(
        "Category",
        validators=[DataRequired(message="Please select a category.")],
    )

    tags = SelectMultipleField(
        "Tags",
        validators=[DataRequired(message="Please select at least one tag.")],
    )

    cover_asset = SelectField(
        "Cover Asset",
        coerce=int_or_none,
        validators=[Optional()],
    )

    inline_assets = SelectMultipleField(
        "Inline Assets",
        coerce=int,
        validators=[Optional()],
    )

    attachment_assets = SelectMultipleField(
        "Attachment Assets",
        coerce=int,
        validators=[Optional()],
    )

    published_at = DateField(
        "Publish Date",
        validators=[Optional()],
        format="%Y-%m-%d",
    )

    preview = SubmitField("Preview")
    submit = SubmitField("Add Article")

    def validate_title(self, field):
        existing = Article.query.filter_by(title=field.data.strip()).first()

        if existing and (
            self.original_article is None or existing.id != self.original_article.id
        ):
            raise ValidationError("An article with this title already exists.")

    def validate_slug(self, field):
        existing = Article.query.filter_by(slug=field.data.strip()).first()

        if existing and (
            self.original_article is None or existing.id != self.original_article.id
        ):
            raise ValidationError("An article with this slug already exists.")

    def validate(self, extra_validators=None):
        is_valid = super().validate(extra_validators=extra_validators)

        if self.status.data == "published" and not self.published_at.data:
            self.published_at.errors.append("Publish date is required when status is Published.")
            is_valid = False

        if self.status.data in ("draft", "archived") and self.published_at.data:
            self.published_at.errors.append("Publish date must be empty unless status is Published.")
            is_valid = False

        return is_valid

class CategoryForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[
            DataRequired(),
            Length(min=2, max=64, message="Name must be between 2 and 64 characters."),
        ],
    )

    slug = StringField(
        "Slug",
        validators=[
            DataRequired(),
            Length(min=2, max=64, message="Slug must be between 2 and 64 characters."),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
            Length(max=128, message="Description cannot be longer than 128 characters."),
        ],
    )

    seo_title = StringField(
        "SEO Title",
        validators=[
            Optional(),
            Length(max=64, message="SEO title cannot be longer than 64 characters."),
        ],
    )

    seo_description = TextAreaField(
        "SEO Description",
        validators=[
            Optional(),
            Length(max=128, message="SEO description cannot be longer than 128 characters."),
        ],
    )

    sort_order = StringField(
        "Sort Order",
        validators=[Optional()],
        default="0",
    )

    submit = SubmitField("Add Category")

    def validate_name(self, field):
        existing = Category.query.filter_by(name=field.data.strip()).first()
        if existing:
            raise ValidationError("A category with this name already exists.")

    def validate_slug(self, field):
        existing = Category.query.filter_by(slug=field.data.strip()).first()
        if existing:
            raise ValidationError("A category with this slug already exists.")

class TagForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[
            DataRequired(),
            Length(min=2, max=64, message="Name must be between 2 and 64 characters."),
        ],
    )

    slug = StringField(
        "Slug",
        validators=[
            DataRequired(),
            Length(min=2, max=64, message="Slug must be between 2 and 64 characters."),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
            Length(max=128, message="Description cannot be longer than 128 characters."),
        ],
    )

    seo_title = StringField(
        "SEO Title",
        validators=[
            Optional(),
            Length(max=64, message="SEO title cannot be longer than 64 characters."),
        ],
    )

    seo_description = TextAreaField(
        "SEO Description",
        validators=[
            Optional(),
            Length(max=128, message="SEO description cannot be longer than 128 characters."),
        ],
    )

    submit = SubmitField("Add Tag")

    def validate_name(self, field):
        existing = Tag.query.filter_by(name=field.data.strip()).first()
        if existing:
            raise ValidationError("A tag with this name already exists.")

    def validate_slug(self, field):
        existing = Tag.query.filter_by(slug=field.data.strip()).first()
        if existing:
            raise ValidationError("A tag with this slug already exists.")

class ProjectForm(FlaskForm):
    def __init__(self, original_project=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_project = original_project

    title = StringField(
        "Title",
        validators=[
            DataRequired(),
            Length(min=5, max=64, message="Title must be between 5 and 64 characters."),
        ],
    )

    slug = StringField(
        "Slug",
        validators=[
            DataRequired(),
            Length(min=5, max=64, message="Slug must be between 5 and 64 characters."),
        ],
    )

    status = SelectField(
        "Status",
        choices=[
            ("draft", "Draft"),
            ("published", "Published"),
            ("archived", "Archived"),
        ],
        validators=[DataRequired()],
    )

    project_state = SelectField(
        "Project State",
        choices=[
            ("planned", "Planned"),
            ("ongoing", "Ongoing"),
            ("finished", "Finished"),
            ("abandoned", "Abandoned"),
        ],
        validators=[DataRequired()],
    )

    platform = StringField(
        "Platform",
        validators=[
            Optional(),
            Length(max=32, message="Platform cannot be longer than 32 characters."),
        ],
    )

    repo_url = StringField(
        "Repository URL",
        validators=[
            Optional(),
            URL(message="Please enter a valid repository URL."),
            Length(max=256, message="Repository URL cannot be longer than 256 characters."),
        ],
    )

    demo_url = StringField(
        "Demo URL",
        validators=[
            Optional(),
            URL(message="Please enter a valid demo URL."),
            Length(max=256, message="Demo URL cannot be longer than 256 characters."),
        ],
    )

    is_featured = BooleanField("Featured")

    excerpt = TextAreaField(
        "Short Description",
        validators=[
            DataRequired(),
            Length(min=20, max=300, message="Short description must be between 20 and 300 characters."),
        ],
    )

    body = TextAreaField(
        "Markdown",
        validators=[
            DataRequired(),
            Length(min=100, message="Markdown must be at least 100 characters."),
        ],
    )

    category = SelectField(
        "Category",
        validators=[DataRequired(message="Please select a category.")],
    )

    tags = SelectMultipleField(
        "Tags",
        validators=[DataRequired(message="Please select at least one tag.")],
    )

    cover_asset = SelectField(
        "Cover Asset",
        coerce=int_or_none,
        validators=[Optional()],
    )

    inline_assets = SelectMultipleField(
        "Inline Assets",
        coerce=int,
        validators=[Optional()],
    )

    attachment_assets = SelectMultipleField(
        "Attachment Assets",
        coerce=int,
        validators=[Optional()],
    )

    published_at = DateField(
        "Publish Date",
        validators=[Optional()],
        format="%Y-%m-%d",
    )

    started_at = DateField(
        "Started Date",
        validators=[Optional()],
        format="%Y-%m-%d",
    )

    completed_at = DateField(
        "Completed Date",
        validators=[Optional()],
        format="%Y-%m-%d",
    )

    preview = SubmitField("Preview")
    submit = SubmitField("Add Project")

    def validate(self, extra_validators=None):
        is_valid = super().validate(extra_validators=extra_validators)

        if self.status.data == "published" and not self.published_at.data:
            self.published_at.errors.append("Publish date is required when status is Published.")
            is_valid = False

        if self.status.data in ("draft", "archived") and self.published_at.data:
            self.published_at.errors.append("Publish date must be empty unless status is Published.")
            is_valid = False

        if self.project_state.data == "planned":
            if self.started_at.data:
                self.started_at.errors.append("Started date must be empty when project state is Planned.")
                is_valid = False
            if self.completed_at.data:
                self.completed_at.errors.append("Completed date must be empty when project state is Planned.")
                is_valid = False

        if self.project_state.data in ("ongoing", "abandoned") and not self.started_at.data:
            self.started_at.errors.append(
                "Started date is required when project state is Ongoing or Abandoned."
            )
            is_valid = False

        if self.project_state.data != "finished" and self.completed_at.data:
            self.completed_at.errors.append(
                "Completed date must be empty unless project state is Finished."
            )
            is_valid = False

        if self.project_state.data == "finished":
            if not self.started_at.data:
                self.started_at.errors.append("Started date is required when project state is Finished.")
                is_valid = False
            if not self.completed_at.data:
                self.completed_at.errors.append("Completed date is required when project state is Finished.")
                is_valid = False

        if self.started_at.data and self.completed_at.data:
            if self.completed_at.data < self.started_at.data:
                self.completed_at.errors.append("Completed date cannot be earlier than started date.")
                is_valid = False

        return is_valid

class AssetForm(FlaskForm):
    ALLOWED_ASSET_EXTENSIONS = [
        # Images
        "jpg", "jpeg", "png", "webp", "gif", "svg", "avif",

        # Documents
        "pdf", "txt", "md", "rtf",

        # Data / structured files
        "json", "csv", "tsv", "xml", "yaml", "yml",

        # Code / text-based assets
        "c", "h", "cpp", "hpp", "py", "js", "ts", "css", "html", "sql",

        # Archives
        "zip", "tar", "gz", "bz2", "xz", "7z",

        # Audio / video
        "mp3", "wav", "ogg", "mp4", "webm",

        # Misc
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
            raise ValueError("Path must start with /uploads/.")

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

        if not raw_path.startswith("/uploads/"):
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

class DeleteForm(FlaskForm):
    submit = SubmitField("Delete")
