import boto3
from dataclasses_json import dataclass_json
from dataclasses import dataclass
from sync.config import Config
from PIL import Image
from io import BytesIO
from pathlib import Path


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


class S3Meta(type):

    def __call__(cls, *args, **kwds):
        return type.__call__(cls, *args, **kwds)

    def upload(cls, item: S3Upload) -> tuple[str, str, str]:
        return cls().upload_file(item.src, item.dst)


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

    def upload_file(self, src, dst) -> tuple[str, str, str]:
        bucket = self._config.storage_bucket_name
        dst = f"maya/{dst}"
        self._client.upload_file(src, bucket, dst)
        img = Image.open(src)
        img.thumbnail(self.THUMB_SIZE)
        byte_io = BytesIO()
        img.save(byte_io, 'WEBP')
        dst_thumb = Path(dst)
        dst_thumb = dst_thumb.parent / f"{dst_thumb.stem}_{'x'.join(map(str, self.THUMB_SIZE))}.webp"
        self._client.upload_fileobj(byte_io, bucket, dst_thumb.as_posix())
        return src, dst, dst_thumb.as_posix()
