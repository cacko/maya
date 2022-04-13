import pickle

from dataclasses_json import dataclass_json, Undefined
from dataclasses import dataclass
from app.storage.models.face import Face as DbFace
from base64 import b64encode
from peewee import *
from PIL import Image
from io import BytesIO


def get_records() -> list['Face']:
    subquery = DbFace.select(fn.MIN(DbFace.id).alias("face_id"), DbFace.name).group_by(DbFace.name).alias("subquery")

    q = DbFace.select().join(subquery, on=(subquery.c.face_id == DbFace.id))

    result = list(q.dicts())
    return result


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Face:
    name: str
    id: int
    image: str

    @classmethod
    def records(cls) -> list[dict]:
        records = get_records()
        for rec in records:
            img = Image.fromarray(pickle.loads(rec["image"]))
            img.thumbnail((100, 100))
            buff2= BytesIO()
            img.save(buff2, "WEBP")
            buff2.seek(0)
            rec["image"] = b64encode(buff2.read())
        models = cls.schema().load(records, many=True)
        return cls.schema().dump(models, many=True)
