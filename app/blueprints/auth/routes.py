from flask import render_template, redirect, url_for, request
from flask_login import current_user, login_user, logout_user

from app import db
from app.forms import LoginForm
from app.models import User
from app.extensions import limiter
from . import auth_bp

import sqlalchemy as sql
import logging

logger = logging.getLogger(__name__)

@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("1/second", override_defaults=False)
@limiter.limit("10/minute", override_defaults=False)
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()

    if not form.validate_on_submit():
        return render_template("auth/login.html", form=form, title="Login")

    # fetch user 
    try:
        user = db.session.scalar(
            sql.select(User).where(User.username == form.username.data)
        )
    except Exception as e:
        logger.error(
            "DB error during login for username=%s: %s",
            form.username.data, str(e),
            exc_info=True,
        )
        return redirect(url_for("auth.login"))

    # unknown user or locked out 
    if user is None or user.is_locked_out():
        logger.warning(
            "Login attempt for locked/unknown user: username=%s ip=%s",
            form.username.data, request.remote_addr,
        )
        form.username.errors.append("Invalid credentials.")
        return render_template("auth/login.html", form=form, title="Login")

    # wrong password 
    if not user.check_password(form.password.data):
        user.login_attempts += 1

        if user.login_attempts >= 5:
            user.lock_user()
            user.login_attempts = 0
            logger.warning(
                "User locked out: username=%s ip=%s",
                user.username, request.remote_addr,
            )
        else:
            logger.warning(
                "Failed login attempt: username=%s ip=%s attempts=%s",
                user.username, request.remote_addr, user.login_attempts,
            )

        db.session.commit()
        form.username.errors.append("Invalid credentials.")
        return render_template("auth/login.html", form=form, title="Login")

    #  success 
    login_user(user, remember=True)
    user.login_attempts = 0
    user.locked_out_until = None
    db.session.commit()

    logger.info(
        "Successful login: user=%s ip=%s",
        user.username, request.remote_addr,
    )
    return redirect(url_for("main.index"))


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))
