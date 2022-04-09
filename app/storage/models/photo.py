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
    def get_records(
            cls,
            page=1,
            query: str = None,
            folder: str = None
    ) -> list['Photo']:
        q = cls.select()
        if query:
            q = q.where(
                (cls.folder ** f"%{query}%") | (cls.full ** f"%{query}%")
            )
        if folder:
            q = q.where(cls.folder == folder)
        q = q.order_by(cls.timestamp.desc()).paginate(page, 100)
        return list(q.dicts())
