from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import exifread
from dataclasses_json import dataclass_json
from dataclasses import dataclass
from exifread.utils import get_gps_coords
from typing import Optional
import re


@dataclass_json
@dataclass
class GPSCoordinates:
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ExifMeta(type):
    DATETIME_FIELDS = ['EXIF DateTimeOriginal', 'Image DateTime']
    DATETIME_FORMAT = ['%Y:%m:%d %H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y:%m:%d:%H:%M:%S']
    WIDTH_FIELD = "EXIF ExifImageLength"
    HEIGHT_FIELD = "EXIF ExifImageWidth"
    _r = re.compile(r'[^\d](20[012]\d{1,})')

    def extract_ts(cls, path: Path):
        matches = cls._r.findall(path.as_posix())
        if not len(matches):
            return datetime(2000, 1, 1, 10, 10, 10, tzinfo=timezone.utc)
        for ts in sorted(matches):
            if len(ts) == 4:
                return datetime(int(ts), 1, 1, 10, 10, 10, tzinfo=timezone.utc)
            if len(ts) == 8:
                return datetime(int(ts[:4]), int(ts[4:6]), int(ts[6:]), 10, 10, 10, tzinfo=timezone.utc)
        return datetime(2000, 1, 1, 10, 10, 10, tzinfo=timezone.utc)


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
            return self.__class__.extract_ts(self.__path)
        ts = next(filter(None, [str(self.__info.get(k)) for k in self.__info.keys() if k in Exif.DATETIME_FIELDS]),
                  None)
        if not ts:
            return self.__class__.extract_ts(self.__path)
        for f in Exif.DATETIME_FORMAT:
            try:
                return datetime.strptime(ts, f).replace(tzinfo=timezone.utc)
            except ValueError:
                pass
        return self.__class__.extract_ts(self.__path)

    def image(self):
        if not self.__image:
            self.__image = Image.open(self.__path.as_posix())
        return self.__image

    @property
    def width(self) -> int:
        if self.__info and Exif.WIDTH_FIELD in self.__info:
            return int(str(self.__info.get(Exif.WIDTH_FIELD)))
        return self.image().width

    @property
    def height(self) -> int:
        if self.__info and Exif.HEIGHT_FIELD in self.__info:
            return int(str(self.__info.get(Exif.HEIGHT_FIELD)))
        return self.image().height

    @property
    def gps(self) -> GPSCoordinates:
        try:
            if self.__info:
                lat, lon = get_gps_coords(self.__info)
                return GPSCoordinates(latitude=lat, longitude=lon)
        except TypeError:
            pass
        return GPSCoordinates()

    def fix_orientation(self):
        tags = self.__info
        if not self.__info:
            return False
        im = Image.open(self.__path.resolve().as_posix())
        fixed = False
        if "Image Orientation" in tags.keys():
            orientation = tags["Image Orientation"]
            val = orientation.values
            if 5 in val:
                val += [4, 6]
            if 7 in val:
                val += [4, 8]
            if 3 in val:
                im = im.transpose(Image.ROTATE_180)
                fixed |= True
            if 4 in val:
                im = im.transpose(Image.FLIP_TOP_BOTTOM)
                fixed |= True
            if 6 in val:
                im = im.transpose(Image.ROTATE_270)
                fixed |= True
            if 8 in val:
                im = im.transpose(Image.ROTATE_90)
                fixed |= True
        if fixed:
            im.save(self.__path.resolve().as_posix())
        return fixed

    def __del__(self):
        if self.__image:
            self.__image.close()
