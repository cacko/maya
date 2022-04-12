__all__ = ["BaseModel"]

from peewee import *
from app.storage import Storage


class BaseModel(Model):
    class Meta:
        database = Storage.db
