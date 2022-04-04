from peewee import *
from app.storage.models import BaseModel


class Photo(BaseModel):
    folder = CharField(index=True, unique=True)
    full = CharField(unique=True)
    thumb = CharField(unique=True)
    timestamp = DateTimeField(index=True)
    width = IntegerField()
    height = IntegerField()
    latitude = FloatField()
    longitude = FloatField()

