from dataclasses_json import dataclass_json, Undefined
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from app.storage.models.photo_face import PhotoFace
from app.storage.models.face import Face
from peewee import *


def get_page(rq) -> int:
    try:
        page = int(rq.args.get("page", 1))
    except ValueError:
        page = 1
    return page


def get_records(
        page: int = 1,
        query: str = None,
        folder: str = None,
        per_page: int = 100,
        face: str = ""
) -> list['Photo']:
    q = Photo.select(fn.SUM)
    if face:
        q = q.join(PhotoFace).join(Face).where(Face.name == face)
    if query:
        q = q.where(
            (Photo.full ** f"%{query}%")
        )
    if folder:
        q = q.where(Photo.folder == folder)

    q = q.order_by(Photo.timestamp.desc()).paginate(page, per_page)
    return list(q.dicts())


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Photo:
    folder: str
    full: str
    thumb: str
    timestamp: datetime
    width: int
    height: int
    latitude: Optional[float]
    longitude: Optional[float]
    faces: Optional[list[str]]

    @classmethod
    def records(cls, request, **kwargs) -> list[dict]:
        records = get_records(
            page=get_page(request),
            query=request.args.get("filter"),
            folder=kwargs.get("folder", request.args.get("folder"))
        )
        models = cls.schema().load(records, many=True)
        return cls.schema().dump(models, many=True)
