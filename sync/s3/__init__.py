import boto3
from dataclasses_json import dataclass_json
from dataclasses import dataclass
from sync.config import Config
from PIL import Image
from io import BytesIO
from pathlib import Path
import filetype


@dataclass_json
@dataclass
class S3Config:
    cloudfront_host: str
    access_key_id: str
    secret_access_key: str
    s3_region: str
    storage_bucket_name: str


@dataclass_json
@dataclass
class S3Upload:
    src: str
    dst: str


def src_key(dst):
    return f"maya/{dst}"


class S3Meta(type):

    def __call__(cls, *args, **kwds):
        return type.__call__(cls, *args, **kwds)

    def upload(cls, item: S3Upload) -> tuple[str, str, str]:
        return cls().upload_file(item.src, item.dst)

    def thumb(cls, item: S3Upload) -> tuple[str, str, str]:
        thumb = cls().upload_thumb(item.src, item.dst)
        return item.src, src_key(item.dst), thumb


class S3(object, metaclass=S3Meta):
    _client: boto3.client = None
    _config: S3Config = None
    THUMB_SIZE = (300, 300)

    def __init__(self) -> None:
        config: S3Config = S3Config.from_dict(Config.namespace("AWS_"))
        self._client = boto3.client(
            service_name='s3',
            region_name=config.s3_region,
            aws_access_key_id=config.access_key_id,
            aws_secret_access_key=config.secret_access_key,
        )
        self._config = config

    def upload_thumb(self, src, dst):
        bucket = self._config.storage_bucket_name
        img = Image.open(src)
        img.thumbnail(self.THUMB_SIZE)
        byte_io = BytesIO()
        img.save(byte_io, 'WEBP')
        byte_io.seek(0)
        dst_thumb = Path(src_key(dst))
        dst_thumb = dst_thumb.parent / f"{dst_thumb.stem}_{'x'.join(map(str, self.THUMB_SIZE))}.webp"
        dst_thumb = dst_thumb.as_posix()
        self._client.upload_fileobj(byte_io, bucket, dst_thumb,
                                    ExtraArgs={'ContentType': 'image/webp', 'ACL': "public-read"})
        return dst_thumb

    def upload_file(self, src, dst) -> tuple[str, str, str]:
        bucket = self._config.storage_bucket_name
        dst = src_key(dst)
        mime = filetype.guess_mime(src)
        self._client.upload_file(src, bucket, dst, ExtraArgs={'ContentType': mime, 'ACL': "public-read"})
        dst_thumb = self.upload_thumb(src, dst)
        return src, dst, dst_thumb
