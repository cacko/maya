from flask import Blueprint, jsonify, request
from app.storage.models import Photo

bp = Blueprint('rest', __name__, url_prefix="/maya/rest")


@bp.route("/photos.json")
def photos():
    page = max(1, int(request.args.get('page', 1)))
    per_page = max(20, int(request.args.get('per_page', 50)))
    records = list(Photo.select().order_by(Photo.timestamp.desc()).paginate(page, per_page).dicts())
    return jsonify(records)
