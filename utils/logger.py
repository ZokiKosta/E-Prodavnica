from flask import session
from models import Log
from database import session as db_session

def log_action(action):
    log = Log(
        action=action,
        user_id=session.get("user_id"),
        username=session.get("username")
    )

    db_session.add(log)
    db_session.commit()