from peewee import *
from app.storage.models import BaseModel
from hashlib import blake2s
from app.face.models import MatchData
import pickle


class Face(BaseModel):
    name = CharField(index=True)
    image = BlobField()
    encoding = BlobField()
    hash = CharField(unique=True, max_length=64)
    is_trained = BooleanField(default=False)

    @classmethod
    def get_hash(cls, data) -> str:
        h = blake2s(digest_size=32)
        h.update(data)
        return h.hexdigest()

    @classmethod
    def get_matched_data(cls):
        return [MatchData(
            encodings=pickle.loads(record.encoding),
            name=record.name,
            face_id=record.id
        ) for record in (cls.select())]
