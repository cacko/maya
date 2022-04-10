from flask import Blueprint, jsonify, request, Response
from app.storage.models import Photo
from hashlib import blake2s
from functools import wraps
from app.rest.models.folder import Folders

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


def get_page(rq) -> int:
    try:
        page = int(rq.args.get("page", 1))
    except ValueError:
        page = 1
    return page


@do_cache()
@bp.route('/photos.json')
def photos():
    records = Photo.get_records(page=get_page(request), query=request.args.get("filter"), folder=request.args.get("folder"));
    return jsonify(records)


@do_cache()
@bp.route('/folders.json')
def folders():
    records = Folders.get_records()
    return jsonify(records)


@do_cache()
@bp.route('/folder/<path:folder>.json')
def get_folder(folder):
    records = Photo.get_records(get_page(request), folder=folder, query=request.args.get("filter"))
    return jsonify(records)
