from flask import Blueprint, render_template
from app.extensions import limiter
from . import project_bp

@project_bp.route("/")
@limiter.limit("1/second", override_defaults=False)
def projects():
    return render_template("projects/projects.html")
