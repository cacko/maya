import boto3
from dataclasses_json import dataclass_json
from dataclasses import dataclass
from PIL import Image
from io import BytesIO
from pathlib import Path
import filetype
from flask import Flask


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
    skip_upload: bool = False


def src_key(dst):
    return f"maya/{dst}"


class S3Meta(type):
    config: S3Config = None

    def __call__(cls, *args, **kwds):
        return type.__call__(cls, *args, **kwds)

    def register(cls, app: 'Flask'):
        cls.config = S3Config.from_dict(app.config.get_namespace("AWS_"))

    def upload(cls, item: S3Upload) -> tuple[str, str, str]:
        return cls().upload_file(item.src, item.dst, item.skip_upload)

    def thumb(cls, item: S3Upload) -> tuple[str, str, str]:
        thumb = cls().upload_thumb(item.src, item.dst, item.skip_upload)
        return item.src, src_key(item.dst), thumb


class S3(object, metaclass=S3Meta):
    _client: boto3.client = None
    THUMB_SIZE = (300, 300)

    def __init__(self) -> None:
        config = self.__class__.config
        self._client = boto3.client(
            service_name='s3',
            region_name=config.s3_region,
            aws_access_key_id=config.access_key_id,
            aws_secret_access_key=config.secret_access_key,
        )
        self._config = config

    def upload_thumb(self, src, dst, skip_upload=False):
        dst_thumb = Path(src_key(dst))
        dst_thumb = dst_thumb.parent / f"{dst_thumb.stem}_{'x'.join(map(str, self.THUMB_SIZE))}.webp"
        dst_thumb = dst_thumb.as_posix()
        if skip_upload:
            return dst_thumb
        bucket = self._config.storage_bucket_name
        img = Image.open(src)
        img.thumbnail(self.THUMB_SIZE)
        byte_io = BytesIO()
        img.save(byte_io, 'WEBP')
        byte_io.seek(0)
        self._client.upload_fileobj(
            byte_io,
            bucket,
            dst_thumb,
            ExtraArgs={'ContentType': 'image/webp', 'ACL': "public-read"}
        )
        return dst_thumb

    def upload_file(self, src, dst, skip_upload=False) -> tuple[str, str, str]:
        mime = filetype.guess_mime(src)
        if not skip_upload:
            bucket = self._config.storage_bucket_name
            self._client.upload_file(src, bucket, src_key(dst), ExtraArgs={'ContentType': mime, 'ACL': "public-read"})
        dst_thumb = self.upload_thumb(src, dst, skip_upload)
        return src, src_key(dst), dst_thumb
