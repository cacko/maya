from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import exifread
from dataclasses_json import dataclass_json
from dataclasses import dataclass
from exifread.utils import get_gps_coords
from typing import Optional


@dataclass_json
@dataclass
class GPSCoordinates:
    latitude: float
    longitude: float


class ExifMeta(type):
    DATETIME_FIELDS = ['DateTimeOriginal', 'DateTime']
    DATETIME_FORMAT = ['%Y:%m:%d %H:%M:%S', '%Y-%m-%d %H:%M:%S']
    WIDTH_FIELD = "ExifImageLength"
    HEIGHT_FIELD = "ExifImageWidth"


class Exif(object, metaclass=ExifMeta):
    __path: Path = None
    __info = None
    __image: Image = None

    def __init__(self, path: Path):
        self.__path = path
        if not self.__path.exists():
            raise FileNotFoundError
        with self.__path.open("rb") as fp:
            self.__info = exifread.process_file(fp, details=False)

    @property
    def timestamp(self) -> datetime:
        if not self.__info:
            return datetime.now(tz=timezone.utc)
        ts = next(filter(None, [self.__info.get(k) for k in self.__info.keys() if k in Exif.DATETIME_FIELDS]), None)
        if not ts:
            return datetime.now(tz=timezone.utc)
        for f in Exif.DATETIME_FORMAT:
            try:
                return datetime.strptime(ts, f).replace(tzinfo=timezone.utc)
            except ValueError:
                pass
        return datetime.now(tz=timezone.utc)

    def image(self):
        if not self.__image:
            self.__image = Image.open(self.__path.as_posix())
        return self.__image

    @property
    def width(self) -> int:
        if self.__info and Exif.WIDTH_FIELD in self.__info:
            return int(self.__info.get(Exif.WIDTH_FIELD))
        return self.image().width

    @property
    def height(self) -> int:
        if self.__info and Exif.HEIGHT_FIELD in self.__info:
            return int(self.__info.get(Exif.HEIGHT_FIELD))
        return self.image().height

    @property
    def gps(self) -> Optional[GPSCoordinates]:
        if self.__info:
            return get_gps_coords(self.__info)
        return None

    def __del__(self):
        if self.__image:
            self.__image.close()
