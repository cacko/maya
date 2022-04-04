from exif import Image as ExifImage
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
from plum.exceptions import UnpackError


class ExifMeta(type):
    DATETIME_FIELDS = ['datetime_original', 'datetime']
    DATETIME_FORMAT = ['%Y:%m:%d %H:%M:%S', '%Y-%m-%d %H:%M:%S']
    WIDTH_FIELD = "pixel_x_dimension"
    HEIGHT_FIELD = "pixel_y_dimension"


class Exif(object, metaclass=ExifMeta):
    __path: Path = None
    __info: ExifImage = None
    __image: Image = None

    def __init__(self, path: Path):
        self.__path = path
        if not self.__path.exists():
            raise FileNotFoundError
        try:
            self.__info = ExifImage(self.__path.as_posix())
        except UnpackError:
            pass

    @property
    def timestamp(self) -> datetime:
        if not self.__info:
            return datetime.now(tz=timezone.utc)
        ts = next(filter(None, [self.__info.get(k) for k in self.__info.list_all() if k in Exif.DATETIME_FIELDS]), None)
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
        if self.__info and Exif.WIDTH_FIELD in self.__info.list_all():
            return int(self.__info.get(Exif.WIDTH_FIELD))
        return self.image().width

    @property
    def height(self) -> int:
        if  self.__info and Exif.HEIGHT_FIELD in self.__info.list_all():
            return int(self.__info.get(Exif.HEIGHT_FIELD))
        return self.image().height

    def __del__(self):
        if self.__image:
            self.__image.close()