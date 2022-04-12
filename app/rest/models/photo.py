from dataclasses_json import dataclass_json, Undefined
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from app.storage.models import Photo as DbPhoto


def get_page(rq) -> int:
    try:
        page = int(rq.args.get("page", 1))
    except ValueError:
        page = 1
    return page


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Photo:
    folder: str
    full: str
    thumb: str
    timestamp: datetime
    width: int
    height: int
    latitude: Optional[float]
    longitude: Optional[float]
    faces: Optional[list[str]]

    @classmethod
    def records(cls, request, **kwargs) -> list[dict]:
        records = DbPhoto.get_records(
            page=get_page(request),
            query=request.args.get("filter"),
            folder=kwargs.get("folder", request.args.get("folder"))
        )
        models = cls.schema().load(records, many=True)
        return cls.schema().dump(models, many=True)
