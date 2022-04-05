from flask import Blueprint, jsonify, request
from app.storage.models import Photo
from hashlib import blake2s

bp = Blueprint('rest', __name__, url_prefix="/maya/rest")


@bp.route("/photos.json")
def photos():
    page = max(1, int(request.args.get('page', 1)))
    per_page = max(20, int(request.args.get('per_page', 50)))
    records = list(Photo.select().order_by(Photo.timestamp.desc()).paginate(page, per_page).dicts())
    etag = blake2s(repr(records).encode()).hexdigest()
    last_modified = max(map(lambda x: x.get("timestamp"), records))
    response = jsonify(records)
    response.headers.set("ETag", etag)
    response.headers.set("Last-Modified", last_modified.strftime(
        "%a, %d %b %Y %H:%M:%S GMT"))
    return response
