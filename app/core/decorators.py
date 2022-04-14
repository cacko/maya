from functools import wraps
from flask import request, abort
from firebase_admin import auth
import firebase_admin

default_app = firebase_admin.initialize_app()


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == "OPTIONS":
            return

        token = request.headers.get("token")

        if not token:
            abort(401)

        user = auth.verify_id_token(token)

        print(user)

        if not user:
            abort(401)

        if user["email"] not in ["spassov@gmail.com"]:
            abort(403)

        return f(*args, **kwargs)

    return decorated_function
