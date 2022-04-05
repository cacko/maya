from flask import Blueprint
from pathlib import Path
from app.upload import Uploader
from app.storage import Storage
from app.local import Local
from app.exif import Exif
import click
from typing import Generator

bp = Blueprint("cli", __name__)


def post_upload(src, full, thumb):
    ex = Exif(Path(src))
    print(src, full, thumb, ex.width, ex.height, ex.timestamp, ex.gps)


@bp.cli.command('process')
@click.argument("path")
def cmd_process(path):
    path = Path(path).resolve()
    if not path.exists():
        raise FileNotFoundError
    it = Local(path)
    uploader = Uploader(len(it), callback=post_upload)
    for f in it:
        src = f.absolute()
        dst = f.relative_to(path)
        uploader.add(src.as_posix(), dst.as_posix())


@bp.cli.command("dbinit")
def cmd_dbinit():
    from app.storage.models import Photo
    with Storage.db as db:
        db.create_tables([Photo])
