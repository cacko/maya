from peewee import *
from app.storage.models import BaseModel


class Face(BaseModel):
    name = CharField(index=True)
    image = BlobField()
    encoding = BlobField()
    is_trained = BooleanField(default=False)
