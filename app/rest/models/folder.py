from app.rest.models import Aggregated
from app.storage.models import Photo
from peewee import fn
from dataclasses_json import dataclass_json
from dataclasses import dataclass
from json import JSONEncoder


@dataclass_json
@dataclass
class FolderItem(JSONEncoder):
    folder: str
    count: int

    def default(self, o):
        return self.to_dict()


class Folder(Aggregated):

    def query(self, *args, **kwargs):
        query = (Photo
                 .select(Photo.folder, fn.COUNT(Photo.folder))
                 .group_by(Photo.folder))
        res = [FolderItem(**x) for x in query.dicts()]
        return res
