from app.rest.models import Aggregated
from app.storage.models.photo import Photo
from peewee import fn
from dataclasses_json import dataclass_json
from dataclasses import dataclass
from json import JSONEncoder
from typing import Optional


@dataclass_json
@dataclass
class FolderItem(JSONEncoder):
    folder: str
    count: int
    sample: Optional[list[Photo]] = None

    def __post_init__(self):
        self.sample = list(Photo.get_records(folder=self.folder, per_page=9))

    def default(self, o):
        return self.to_dict()


class Folders(Aggregated):

    def query(self, *args, **kwargs):
        query = (Photo
                 .select(Photo.folder, fn.COUNT(Photo.folder))
                 .group_by(Photo.folder))
        res = [FolderItem(**x) for x in query.dicts()]
        return res
