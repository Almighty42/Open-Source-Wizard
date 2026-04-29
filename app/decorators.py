from flask import url_for, redirect
from functools import wraps

from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def check_if_admin(*args, **kwargs):
        if not current_user.is_admin:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return check_if_admin
