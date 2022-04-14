from functools import wraps
from flask import request, abort


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == "OPTIONS":
            return

        token = request.headers("token");

        user = User.from_request(request)

        if not user:
            abort(401)

        return f(*args, **kwargs)

    return decorated_function
