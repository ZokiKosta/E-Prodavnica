from functools import wraps
from flask import redirect, url_for, flash, session

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in first", "error")
            return redirect(url_for("login"))

        if not session.get("is_admin"):
            return "Unauthorized", 403

        return f(*args, **kwargs)

    return decorated_function