from flask import Blueprint, jsonify, request, Response, session
from app.rest.models.photo import Photo as RestPhoto
from app.rest.models.face import Face as RestFace
from hashlib import blake2s
from functools import wraps
from app.rest.models.folder import Folders
from app.core.decorators import auth_required

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
@bp.route('/photos.json')
@auth_required
def photos():
    return jsonify(RestPhoto.records(request))


@do_cache()
@bp.route('/folders.json')
@auth_required
def folders():
    records = Folders.get_records()
    return jsonify(records)


@do_cache()
@bp.route('/folder/<path:folder>.json')
@auth_required
def get_folder(folder):
    return jsonify(RestPhoto.records(request, folder=folder))


@do_cache()
@bp.route('/face/<name>.json')
@auth_required
def face(name):
    return jsonify(RestPhoto.records(request, face=name))


@bp.route('/faces.json')
@auth_required
def faces():
    return jsonify(RestFace.records())

