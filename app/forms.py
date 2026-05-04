from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    StringField,
    PasswordField,
    TextAreaField,
    SelectField,
    SelectMultipleField,
    SubmitField,
)
from wtforms.validators import DataRequired, Optional, Length, ValidationError
from app.models import Article , Category, Tag

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

    def _validate_published_at(self, field):
        if self.status.data in {"draft", "archived"} and field.data:
            raise ValidationError("Draft and archived articles cannot have a publish date.")

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

class DeleteForm(FlaskForm):
    submit = SubmitField("Delete")
