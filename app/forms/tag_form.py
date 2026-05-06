from app.models import Tag

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    SubmitField,
)
from wtforms.validators import DataRequired, Optional, Length, ValidationError

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
