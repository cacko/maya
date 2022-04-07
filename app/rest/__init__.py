from flask import Blueprint, jsonify, request, Response
from app.storage.models import Photo
from hashlib import blake2s
from functools import wraps

bp = Blueprint('rest', __name__, url_prefix="/maya/rest")


def do_cache():
    def fwrap(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            rsp: Response = f(*args, **kwargs)
            json = rsp.json
            etag = blake2s(repr(json).encode()).hexdigest()
            last_modified = max(map(lambda x: x.get("timestamp"), json))
            rsp.headers.set("ETag", etag)
            rsp.headers.set("Last-Modified", last_modified.strftime(
                "%a, %d %b %Y %H:%M:%S GMT"))
            return rsp

        return wrapped_f

    return fwrap


@do_cache()
@bp.route('/photos', defaults={'page': 1})
@bp.route('/photos/<int:page>')
def photos(page):
    records = Photo.get_records(page)
    return jsonify(records)


@do_cache()
@bp.route('/photos/<query>', defaults={'page': 1})
@bp.route('/photos/<query>/<int:page>')
def query_photos(query, page):
    records = Photo.get_records(page, query)
    return records
