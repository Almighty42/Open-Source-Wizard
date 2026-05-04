from typing import List, Optional
from enum import Enum
from datetime import datetime
from app.models.base import Status,Role
from app.utils import utc_now
from app.extensions import db
import sqlalchemy as sql
import sqlalchemy.orm as orm

class ProjectState(str, Enum):
    abandoned = "abandoned"
    planned = "planned"
    ongoing = "ongoing"
    finalized = "finalized"

class Project(db.Model):
    __tablename__ = "projects"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    title: orm.Mapped[str] = orm.mapped_column(sql.String(64), unique=True, nullable=False)
    created_at: orm.Mapped[datetime] = orm.mapped_column(sql.DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: orm.Mapped[datetime] = orm.mapped_column(sql.DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    body: orm.Mapped[str] = orm.mapped_column(sql.Text(), nullable=False)
    status: orm.Mapped[Status] = orm.mapped_column(sql.Enum(Status, name="project_status"), nullable=False)
    published_at: orm.Mapped[datetime | None] = orm.mapped_column(sql.DateTime(timezone=True), nullable=True)
    author_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    slug: orm.Mapped[str] = orm.mapped_column(sql.String(64), unique=True, nullable=False)
    repo_url: orm.Mapped[str | None] = orm.mapped_column(sql.String(256), nullable=True)
    demo_url: orm.Mapped[str | None] = orm.mapped_column(sql.String(256), nullable=True)
    is_featured: orm.Mapped[bool] = orm.mapped_column(default=False, nullable=False)
    platform: orm.Mapped[str | None] = orm.mapped_column(sql.String(32), nullable=True)
    project_state: orm.Mapped[ProjectState] = orm.mapped_column(sql.Enum(ProjectState, name="project_state"), nullable=False)
    started_at: orm.Mapped[datetime | None] = orm.mapped_column(sql.DateTime(timezone=True), nullable=True)
    completed_at: orm.Mapped[datetime | None] = orm.mapped_column(sql.DateTime(timezone=True), nullable=True)
    seo_title: orm.Mapped[str | None] = orm.mapped_column(sql.String(64), unique=True, nullable=True)
    seo_description: orm.Mapped[str | None] = orm.mapped_column(sql.Text(), nullable=True)
    excerpt: orm.Mapped[str] = orm.mapped_column(sql.Text(), nullable=False)

    project_tags: orm.Mapped[List["ProjectTag"]] = orm.relationship(back_populates="project", cascade="all, delete-orphan")
    project_categories: orm.Mapped[List["ProjectCategory"]] = orm.relationship(back_populates="project", cascade="all, delete-orphan")
    project_assets: orm.Mapped[List["ProjectAsset"]] = orm.relationship(back_populates="project", cascade="all, delete-orphan")

    tags: orm.Mapped[List["Tag"]] = orm.relationship(
            secondary="project_tags",
            viewonly=True,
            order_by="ProjectTag.sort_order"
            )
    categories: orm.Mapped[List["Category"]] = orm.relationship(
            secondary="project_categories",
            viewonly=True,
            )
    assets: orm.Mapped[List["Asset"]] = orm.relationship(
            secondary="project_assets",
            viewonly=True,
            )
    author: orm.Mapped[Optional["User"]] = orm.relationship(back_populates="projects")

    @property
    def primary_category(self):
        for ac in self.project_categories:
            if ac.is_primary:
                return ac.category
        return self.categories[0] if self.categories else None

class ProjectCategory(db.Model):
    __tablename__ = "project_categories"

    project_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey("projects.id", ondelete="CASCADE"),primary_key=True)
    category_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey("categories.id", ondelete="CASCADE"),primary_key=True)
    sort_order: orm.Mapped[int] = orm.mapped_column(default=0, nullable=False)
    is_primary: orm.Mapped[bool] = orm.mapped_column(default=False, nullable=False)

    project: orm.Mapped["Project"] = orm.relationship(back_populates="project_categories")
    category: orm.Mapped["Category"] = orm.relationship(back_populates="project_categories")


class ProjectTag(db.Model):
    __tablename__ = "project_tags"

    project_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey("projects.id", ondelete="CASCADE"),primary_key=True)
    tag_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey("tags.id", ondelete="CASCADE"),primary_key=True)
    sort_order: orm.Mapped[int] = orm.mapped_column(default=0, nullable=False)

    project: orm.Mapped["Project"] = orm.relationship(back_populates="project_tags")
    tag: orm.Mapped["Tag"] = orm.relationship(back_populates="project_tags")

class ProjectAsset(db.Model):
    __tablename__ = "project_assets"

    project_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey("projects.id", ondelete="CASCADE"),primary_key=True)
    asset_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey("assets.id", ondelete="CASCADE"),primary_key=True)
    role: orm.Mapped[Role] = orm.mapped_column(sql.Enum(Role, name="project_asset_role"), nullable=False)
    is_cover: orm.Mapped[bool] = orm.mapped_column(default=False, nullable=False)
    alt_override: orm.Mapped[str | None] = orm.mapped_column(sql.String(64), nullable=True)
    caption_override: orm.Mapped[str | None] = orm.mapped_column(sql.String(64), nullable=True)

    project: orm.Mapped["Project"] = orm.relationship(back_populates="project_assets")
    asset: orm.Mapped["Asset"] = orm.relationship(back_populates="project_assets")
