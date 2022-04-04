__all__ = ["BaseModel", "Photo"]

from peewee import *
from app.storage import Storage


class BaseModel(Model):
    class Meta:
        database = Storage.db


from app.storage.models.photo import Photo
