from typing import List
from enum import Enum
from datetime import datetime
from app.utils import utc_now
from app.extensions import db
import sqlalchemy as sql
import sqlalchemy.orm as orm

class Status(str, Enum):
    draft = "draft"
    published = "published"
    archived = "archived"

class Role(str, Enum):
    cover       = "cover"        # Hero/thumbnail image (og:image, list cards)
    inline      = "inline"       # Embedded inside the body markdown
    gallery     = "gallery"      # Part of a photo/screenshot gallery section
    attachment  = "attachment"   # Downloadable file (PDF, zip, schematic)
    diagram     = "diagram"      # Circuit diagram, flowchart, architecture drawing
    video       = "video"        # Demo video / walkthrough

class Category(db.Model):
    __tablename__ = "categories"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    name: orm.Mapped[str] = orm.mapped_column(sql.String(64), unique=True, nullable=False)
    slug: orm.Mapped[str] = orm.mapped_column(sql.String(64), unique=True, nullable=False)
    description: orm.Mapped[str | None] = orm.mapped_column(sql.String(128), nullable=True)
    seo_title: orm.Mapped[str | None] = orm.mapped_column(sql.String(64), nullable=True)
    seo_description: orm.Mapped[str | None] = orm.mapped_column(sql.String(128), nullable=True)
    created_at: orm.Mapped[datetime] = orm.mapped_column(sql.DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: orm.Mapped[datetime] = orm.mapped_column(sql.DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    sort_order: orm.Mapped[int] = orm.mapped_column(sql.Integer, default=0, nullable=False, index=True)

    article_categories: orm.Mapped[List["ArticleCategory"]] = orm.relationship(back_populates="category")
    project_categories: orm.Mapped[List["ProjectCategory"]] = orm.relationship(back_populates="category")

class Tag(db.Model):
    __tablename__ = "tags"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    name: orm.Mapped[str] = orm.mapped_column(sql.String(64), unique=True, nullable=False)
    slug: orm.Mapped[str] = orm.mapped_column(sql.String(64), unique=True, nullable=False)
    description: orm.Mapped[str | None] = orm.mapped_column(sql.String(128), nullable=True)
    seo_title: orm.Mapped[str | None] = orm.mapped_column(sql.String(64), nullable=True)
    seo_description: orm.Mapped[str | None] = orm.mapped_column(sql.String(128), nullable=True)
    created_at: orm.Mapped[datetime] = orm.mapped_column(sql.DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: orm.Mapped[datetime] = orm.mapped_column(sql.DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    article_tags: orm.Mapped[List["ArticleTag"]] = orm.relationship(back_populates="tag")
    project_tags: orm.Mapped[List["ProjectTag"]] = orm.relationship(back_populates="tag")

class Asset(db.Model):
    __tablename__ = "assets"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    path: orm.Mapped[str] = orm.mapped_column(sql.String(128), unique=True, nullable=False)
    alt_text: orm.Mapped[str | None] = orm.mapped_column(sql.String(64), nullable=True)
    caption: orm.Mapped[str | None] = orm.mapped_column(sql.String(64), nullable=True)
    created_at: orm.Mapped[datetime] = orm.mapped_column(sql.DateTime(timezone=True), default=utc_now, nullable=False)

    article_assets: orm.Mapped[List["ArticleAsset"]] = orm.relationship(back_populates="asset")
    project_assets: orm.Mapped[List["ProjectAsset"]] = orm.relationship(back_populates="asset")
