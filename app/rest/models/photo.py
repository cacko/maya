from dataclasses_json import dataclass_json, Undefined, config
from marshmallow import fields
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from app.storage.models.photo import Photo as DbPhoto
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
    q = DbPhoto.select(
        DbPhoto,
        fn.STRING_AGG(Face.name, ",").alias("faces"),
        fn.STRING_AGG(PhotoFace.location, "|").alias("locations")
    )

    if face:
        q = q.join(PhotoFace).join(Face)
        q = q.where(Face.name == face)
    else:
        q = q.join(PhotoFace, JOIN.LEFT_OUTER).join(Face, JOIN.LEFT_OUTER)

    if query:
        q = q.where(
            (DbPhoto.full ** f"%{query}%")
        )
    if folder:
        q = q.where(DbPhoto.folder == folder)

    q = q.group_by(DbPhoto.id)

    q = q.order_by(DbPhoto.timestamp.desc()).paginate(page, per_page)
    result = list(q.dicts())
    return result


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Photo:
    id: int
    folder: str
    full: str
    thumb: str
    timestamp: datetime
    width: int
    height: int
    latitude: Optional[float]
    longitude: Optional[float]
    faces: Optional[str]
    locations: Optional[str]

    @classmethod
    def records(cls, request, **kwargs) -> list[dict]:
        records = get_records(
            page=get_page(request),
            query=request.args.get("filter"),
            folder=kwargs.get("folder", request.args.get("folder")),
            face=kwargs.get("face", request.args.get("face")),
        )
        for rec in records:
            rec["timestamp"] = rec.get("timestamp").timestamp()
        models = cls.schema().load(records, many=True)
        return cls.schema().dump(models, many=True)
