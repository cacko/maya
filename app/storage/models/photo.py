from peewee import *
from app.storage.models import BaseModel, Face, PhotoFace


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
    faces = ManyToManyField(Face, backref='photos')

    @classmethod
    def get_records(
            cls,
            page: int = 1,
            query: str = None,
            folder: str = None,
            per_page: int = 100,
            face: str = ""
    ) -> list['Photo']:
        q = cls.select(fn.SUM)
        if face:
            q = q.join(PhotoFace).join(Face).where(Face.name == face)
        if query:
            q = q.where(
                (cls.full ** f"%{query}%")
            )
        if folder:
            q = q.where(cls.folder == folder)

        q = q.order_by(cls.timestamp.desc()).paginate(page, per_page)
        return list(q.dicts())

