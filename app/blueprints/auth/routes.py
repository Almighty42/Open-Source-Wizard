from flask import render_template, redirect, url_for
from app import db
from app.forms import LoginForm
from app.models import User
from app.extensions import limiter
from . import auth_bp

from flask_login import current_user, login_user, logout_user
import sqlalchemy as sql

@auth_bp.route("/login", methods=['GET', 'POST'])
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
            return redirect(url_for("auth.login"))

        if user is not None and not user.is_locked_out():
            if user.check_password(form.password.data):
                login_user(user, remember=True)
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
                return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('auth.login'))
    return render_template("auth/login.html", form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
