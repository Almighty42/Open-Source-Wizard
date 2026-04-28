import click
from flask import Blueprint
from app.seeders import UserSeeder, TagSeeder, CategorySeeder, ActivitySeeder

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

@seed_bp.cli.command("activities")
@click.option("--count", default=40, help="Number of activity records to generate")
def seed_activites(count):
    ActivitySeeder(count=count).run()
