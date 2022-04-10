from peewee import *
from app.storage.models import BaseModel
from .photo import Photo
from .face import Face


class PhotoFace(BaseModel):
    photo_id = ForeignKeyField(Photo)
    face_id = ForeignKeyField(Face)

    class Meta:
        primary_key = CompositeKey('photo_id', 'face_id')
