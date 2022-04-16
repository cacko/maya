from functools import wraps
from flask import request, abort, current_app, session
from firebase_admin import auth
import firebase_admin

firebase_admin.initialize_app()


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == "OPTIONS":
            return

        token = request.headers.get("token")

        if not token:
            abort(401)



        print(session)

        if session.get("token") != token:

            print("check token", session.get("token"), token)

            user = auth.verify_id_token(token)

            if not user:
                abort(401)

            auth_config = current_app.config.get_namespace("AUTH_")

            if user["email"] not in auth_config.get("users", []):
                abort(403)

            session["token"] = token

        return f(*args, **kwargs)

    return decorated_function
