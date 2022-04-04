__all__ = ["BaseModel", "Photo"]

from peewee import *
from api.storage import Storage


class BaseModel(Model):
    class Meta:
        database = Storage.db


from api.storage.models.photo import Photo
