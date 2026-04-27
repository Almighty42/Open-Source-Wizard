from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, logout_user, login_user
from app.forms import LoginForm
from app.models import User
from app import db, login_manager
import sqlalchemy as sql
from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

main = Blueprint("main", __name__)

def admin_required(f):
    @wraps(f)
    def check_if_admin(*args, **kwargs):
        if not current_user.is_admin:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return check_if_admin

limiter = Limiter(
        get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",
)

@main.route("/")
@main.route("/index")
@limiter.limit("1/second", override_defaults=False)
def index():

    articles = [
            {
                "category": "Software Development / Embedded",
                "title": "Use of AI in Embedded Development",
                "body": "Lorem ipsum dolor sit amet consectetur adipiscing elit. Sit amet consectetur adipiscing elit quisque faucibus ex. Adipiscing elit quisque faucibus ex sapien vitae pellentesque.Lorem ipsum dolor sit amet consectetur adipiscing elit. \n\n Lorem ipsum dolor sit amet consectetur adipiscing elit. Adipiscing elit quisque faucibus ex sapien vitae pellentesque.Lorem ipsum dolor sit amet consectetur adipiscing elit...",
                "tags": [
                    "Embedded",
                    "Topic Explained",
                    "C Programming"
                ],
                "date": "02 APR 2026",
                "read_time": "12 MIN READ"
            },
            {
                "category": "Electronics",
                "title": "How to use a solder properly",
                "body": "Lorem ipsum dolor sit amet consectetur adipiscing elit. Sit amet consectetur adipiscing elit quisque faucibus ex. Adipiscing elit quisque faucibus ex sapien vitae pellentesque.Lorem ipsum dolor sit amet consectetur adipiscing elit. \n\n Lorem ipsum dolor sit amet consectetur adipiscing elit. Adipiscing elit quisque faucibus ex sapien vitae pellentesque.Lorem ipsum dolor sit amet consectetur adipiscing elit...",
                "tags": [
                    "Electronics",
                    "Hands-on"
                ],
                "date": "13 JAN 2026",
                "read_time": "9 MIN READ"
            }
    ]

    projects = [ 
            {
            "title": "USART Driver from scratch",
            "body": "Lorem ipsum dolor sit amet consectetur adipiscing elit. Sit amet consectetur adipiscing elit quisque faucibus ex. Adipiscing elit quisque faucibus ex sapien vitae pellentesque.Lorem ipsum dolor sit amet consectetur adipiscing elit. \n\n Lorem ipsum dolor sit amet consectetur adipiscing elit. Adipiscing elit quisque faucibus ex sapien vitae pellentesque.Lorem ipsum dolor sit amet consectetur adipiscing elit...",
            "tags": [
                "Embedded",
                "Topic Explained",
                "C Programming"
                ],
            "category": "Software development / Embedded",
            "img": "assets/placeholder.png"
            },

            {
            "title": "Custom RF emmiter",
            "body": "Lorem ipsum dolor sit amet consectetur adipiscing elit. Sit amet consectetur adipiscing elit quisque faucibus ex. Adipiscing elit quisque faucibus ex sapien vitae pellentesque.Lorem ipsum dolor sit amet consectetur adipiscing elit. \n\n Lorem ipsum dolor sit amet consectetur adipiscing elit. Adipiscing elit quisque faucibus ex sapien vitae pellentesque.Lorem ipsum dolor sit amet consectetur adipiscing elit...",
            "tags": [
                "RF",
                "Electronics"
                ],
            "category": "Hardware development / RF",
            "img": "assets/placeholder.png"
            },

            {
            "title": "SPI Driver from scratch",
            "body": "Lorem ipsum dolor sit amet consectetur adipiscing elit. Sit amet consectetur adipiscing elit quisque faucibus ex. Adipiscing elit quisque faucibus ex sapien vitae pellentesque.Lorem ipsum dolor sit amet consectetur adipiscing elit. \n\n Lorem ipsum dolor sit amet consectetur adipiscing elit. Adipiscing elit quisque faucibus ex sapien vitae pellentesque.Lorem ipsum dolor sit amet consectetur adipiscing elit...",
            "tags": [
                "Embedded",
                "Topic Explained"
                ],
            "category": "Software development / Embedded",
            "img": "assets/placeholder.png"
            }
    ]

    return render_template("index.html", articles=articles, projects=projects)

@main.route("/articles")
@limiter.limit("1/second", override_defaults=False)
def articles():
    return render_template("articles.html")

@main.route("/projects")
@limiter.limit("1/second", override_defaults=False)
def projects():
    return render_template("projects.html")

@main.route("/about")
@limiter.limit("1/second", override_defaults=False)
def about():
    return render_template("about.html")

@main.route("/login", methods=['GET', 'POST'])
@limiter.limit("1/second", override_defaults=False)
@limiter.limit("10/minute", override_defaults=False)
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if form.validate_on_submit():
        try:
            user = db.session.scalar(sql.select(User).where(User.username == form.username.data))
        except:
            return redirect(url_for("main.login"))

        if user is not None and not user.is_locked_out():
            if user.check_password(form.password.data):
                login_user(user)
                user.login_attempts = 0
                user.locked_out_until = None
                db.session.commit()
                return redirect(url_for("main.index"))
            else:
                user.login_attempts += 1
                if user.login_attempts >= 5:
                    user.lock_user()
                    user.login_attempts = 0
                db.session.commit()
                return redirect(url_for('main.login'))
        else:
            return redirect(url_for('main.login'))
    return render_template("login.html", form=form)

@main.route('/logout')
@limiter.limit("1/second", override_defaults=False)
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("main.index"))
