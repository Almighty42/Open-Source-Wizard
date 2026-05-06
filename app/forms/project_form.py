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
from wtforms.validators import DataRequired, Optional, Length, URL

def int_or_none(value):
    if value in (None, "", "None"):
        return None
    return int(value)

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
