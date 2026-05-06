from app.models import Article 

from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    StringField,
    TextAreaField,
    SelectField,
    SelectMultipleField,
    SubmitField,
    BooleanField,
)
from wtforms.validators import DataRequired, Optional, Length, ValidationError

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
