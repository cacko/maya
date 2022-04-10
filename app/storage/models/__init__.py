__all__ = ["BaseModel", "Photo", "Face", "PhotoFace"]

from peewee import *
from app.storage import Storage


class BaseModel(Model):
    class Meta:
        database = Storage.db


from app.storage.models.photo import Photo
from app.storage.models.face import Face
from app.storage.models.photo_face import PhotoFace
