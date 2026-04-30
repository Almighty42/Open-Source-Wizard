from typing import List, Optional
from datetime import datetime
from app.models.base import Status, Role
from app.models.utils import utc_now
from app.extensions import db
import sqlalchemy as sql
import sqlalchemy.orm as orm

class Article(db.Model):
    __tablename__ = "articles"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    title: orm.Mapped[str] = orm.mapped_column(sql.String(64), unique=True, nullable=False)
    created_at: orm.Mapped[datetime] = orm.mapped_column(sql.DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: orm.Mapped[datetime] = orm.mapped_column(sql.DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    read_time: orm.Mapped[int] = orm.mapped_column(nullable=False)
    body: orm.Mapped[str] = orm.mapped_column(sql.Text(), nullable=False)
    status: orm.Mapped[Status] = orm.mapped_column(sql.Enum(Status, name="article_status"), nullable=False)
    published_at: orm.Mapped[datetime | None] = orm.mapped_column(sql.DateTime(timezone=True), nullable=True)
    author_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    slug: orm.Mapped[str] = orm.mapped_column(sql.String(64), unique=True, nullable=False)
    is_featured: orm.Mapped[bool] = orm.mapped_column(default=False, nullable=False)
    seo_title: orm.Mapped[str | None] = orm.mapped_column(sql.String(64), unique=True, nullable=True)
    seo_description: orm.Mapped[str | None] = orm.mapped_column(sql.Text(), nullable=True)
    excerpt: orm.Mapped[str] = orm.mapped_column(sql.Text(), nullable=False)

    article_tags: orm.Mapped[List["ArticleTag"]] = orm.relationship(back_populates="article", cascade="all, delete-orphan")
    article_categories: orm.Mapped[List["ArticleCategory"]] = orm.relationship(back_populates="article", cascade="all, delete-orphan")
    article_assets: orm.Mapped[List["ArticleAsset"]] = orm.relationship(back_populates="article", cascade="all, delete-orphan")

    tags: orm.Mapped[List["Tag"]] = orm.relationship(
            secondary="article_tags",
            viewonly=True,
            order_by="ArticleTag.sort_order"
            )
    categories: orm.Mapped[List["Category"]] = orm.relationship(
            secondary="article_categories",
            viewonly=True,
            )
    assets: orm.Mapped[List["Asset"]] = orm.relationship(
            secondary="article_assets",
            viewonly=True,
            )
    author: orm.Mapped[Optional["User"]] = orm.relationship(back_populates="articles")

    @property
    def primary_category(self):
        for ac in self.article_categories:
            if ac.is_primary:
                return ac.category
        return self.categories[0] if self.categories else None

class ArticleCategory(db.Model):
    __tablename__ = "article_categories"

    article_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey("articles.id", ondelete="CASCADE"),primary_key=True)
    category_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey("categories.id", ondelete="CASCADE"),primary_key=True)
    sort_order: orm.Mapped[int] = orm.mapped_column(default=0, nullable=False)
    is_primary: orm.Mapped[bool] = orm.mapped_column(default=False, nullable=False)

    article: orm.Mapped["Article"] = orm.relationship(back_populates="article_categories")
    category: orm.Mapped["Category"] = orm.relationship(back_populates="article_categories")

class ArticleTag(db.Model):
    __tablename__ = "article_tags"

    article_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey("articles.id", ondelete="CASCADE"),primary_key=True)
    tag_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey("tags.id", ondelete="CASCADE"),primary_key=True)
    sort_order: orm.Mapped[int] = orm.mapped_column(default=0, nullable=False)

    article: orm.Mapped["Article"] = orm.relationship(back_populates="article_tags")
    tag: orm.Mapped["Tag"] = orm.relationship(back_populates="article_tags")

class ArticleAsset(db.Model):
    __tablename__ = "article_assets"

    article_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey("articles.id", ondelete="CASCADE"),primary_key=True)
    asset_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey("assets.id", ondelete="CASCADE"),primary_key=True)
    role: orm.Mapped[Role] = orm.mapped_column(sql.Enum(Role, name="article_asset_role"), nullable=False)
    is_cover: orm.Mapped[bool] = orm.mapped_column(default=False, nullable=False)
    alt_override: orm.Mapped[str | None] = orm.mapped_column(sql.String(64), nullable=True)
    caption_override: orm.Mapped[str | None] = orm.mapped_column(sql.String(64), nullable=True)

    article: orm.Mapped["Article"] = orm.relationship(back_populates="article_assets")
    asset: orm.Mapped["Asset"] = orm.relationship(back_populates="article_assets")
