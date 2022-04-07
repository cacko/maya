from peewee import *
from app.storage.models import BaseModel


class Photo(BaseModel):
    folder = CharField(index=True)
    full = CharField(unique=True)
    thumb = CharField(unique=True)
    timestamp = DateTimeField(index=True)
    width = IntegerField()
    height = IntegerField()
    latitude = FloatField(null=True)
    longitude = FloatField(null=True)

    @classmethod
    def get_records(cls, page=1, query: str = None) -> list['Photo']:
        q = cls.select()
        if query:
            q.where(cls.folder ** query)
        q = q.order_by(cls.timestamp.desc()).paginate(page, 50)
        return list(q.dicts())
