from functools import wraps
from flask import redirect, url_for, flash, session as flask_session
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not flask_session.get("user_id"):
            flash("Please log in first", "error")
            return redirect(url_for("login"))

        if not flask_session.get("is_admin"):
            return "Unauthorized", 403

        return f(*args, **kwargs)

    return decorated_function

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not flask_session.get("user_id"):
            flash("You must be logged in to access this page.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function