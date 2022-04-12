from peewee import *
from app.storage.models import BaseModel
from app.storage.models.face import Face


class Photo(BaseModel):
    folder = CharField(index=True)
    full = CharField(unique=True)
    thumb = CharField(unique=True)
    timestamp = DateTimeField(index=True)
    width = IntegerField()
    height = IntegerField()
    latitude = FloatField(null=True)
    longitude = FloatField(null=True)
    processed = BooleanField(default=False)


