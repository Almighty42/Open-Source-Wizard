import click
from flask import Blueprint
from app.seeders import UserSeeder, TagSeeder, CategorySeeder, ActivitySeeder, AssetSeeder, ProjectSeeder, ArticleSeeder
from app.models import ArticleAsset, ArticleTag, ArticleCategory, Article, Project, ProjectAsset, ProjectCategory, ProjectTag, Tag, Category, Asset, Activity
from app import db

seed_bp = Blueprint("seed", __name__)

@seed_bp.cli.command("user")
def seed_user():
    UserSeeder().run()

@seed_bp.cli.command("tags")
def seed_tags():
    TagSeeder().run()

@seed_bp.cli.command("categories")
def seed_categories():
    CategorySeeder().run()

@seed_bp.cli.command("assets")
def seed_assets():
    AssetSeeder().run()

@seed_bp.cli.command("activities")
@click.option("--count", default=40, help="Number of activity records to generate")
def seed_activites(count):
    ActivitySeeder(count=count).run()

@seed_bp.cli.command("articles")
def seed_articles():
    ArticleSeeder().run()

@seed_bp.cli.command("projects")
def seed_projects():
    ProjectSeeder().run()

@seed_bp.cli.command("all")
def seed_all():
    UserSeeder().run()
    TagSeeder().run()
    CategorySeeder().run()
    AssetSeeder().run()
    ArticleSeeder().run()
    ProjectSeeder().run()
    ActivitySeeder().run()

@seed_bp.cli.command("wipe")
def wipe():
    db.session.query(Activity).delete()  
    db.session.query(ArticleAsset).delete()
    db.session.query(ArticleTag).delete()
    db.session.query(ArticleCategory).delete()
    db.session.query(Article).delete()

    db.session.query(ProjectAsset).delete()
    db.session.query(ProjectTag).delete()
    db.session.query(ProjectCategory).delete()
    db.session.query(Project).delete()

    db.session.query(Category).delete()
    db.session.query(Tag).delete()
    db.session.query(Asset).delete()

    db.session.commit()
    print("Wiped.")
